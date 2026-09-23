"""Package pinned KiCad projects and fabrication candidates; no fabrication submission."""
from pathlib import Path
import json,re,shutil,subprocess,hashlib
import pcbnew as pcb
ROOT=Path(__file__).resolve().parents[1];LIB=Path('D:/ProgramFiles/KiCad/10.0/share/kicad');CLI=Path('D:/ProgramFiles/KiCad/10.0/bin/kicad-cli.exe')
NAMES={'sensor_revM_side':'PoseDoll_AS5048A_revM_side','sensor_revM_large_sh':'PoseDoll_AS5048A_revM_large_sh','regional_revM':'PoseDoll_PD41_Regional_revM','power_revM':'PoseDoll_PD41_Power_revM'}

def run(args):
 r=subprocess.run([str(CLI),*map(str,args)],capture_output=True,text=True,encoding='utf-8',errors='replace')
 if r.returncode:raise RuntimeError((args,r.returncode,r.stdout[-1800:],r.stderr[-1200:]))
 return r.stdout

def package(kind,name):
 source=ROOT/'electronics'/kind;dest=ROOT/'generated/revM/electronics'/kind;dest.mkdir(parents=True,exist_ok=True)
 for ext in ('kicad_sch','kicad_pcb','kicad_pro'):shutil.copy2(source/(name+'.'+ext),dest/(name+'.'+ext))
 text=(dest/(name+'.kicad_sch')).read_text(encoding='utf-8')
 libs=sorted(set(re.findall(r'\(lib_id "([^:"]+):',text)));entries=[]
 for lib in libs:
  src=source/'symbols'/(lib+'.kicad_sym')
  if not src.exists():src=LIB/'symbols'/(lib+'.kicad_sym')
  target=dest/'symbols'/src.name;target.parent.mkdir(exist_ok=True);shutil.copy2(src,target)
  entries.append(f'(lib (name "{lib}") (type "KiCad") (uri "${{KIPRJMOD}}/symbols/{src.name}") (options "") (descr "Pinned KiCad 10 symbol library"))')
 (dest/'sym-lib-table').write_text('(sym_lib_table '+''.join(entries)+')',encoding='utf-8')
 board=pcb.LoadBoard(str(dest/(name+'.kicad_pcb')));fplibs=set();missing=[]
 for fp in board.GetFootprints():
  lib=str(fp.GetFPID().GetLibNickname());part=str(fp.GetFPID().GetLibItemName());fplibs.add(lib)
  src=source/(lib+'.pretty')/(part+'.kicad_mod')
  if not src.exists():src=LIB/'footprints'/(lib+'.pretty')/(part+'.kicad_mod')
  if not src.exists():raise ValueError(('missing footprint source',lib,part))
  dst=dest/'footprints'/(lib+'.pretty')/src.name;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
  if kind.startswith('sensor_') and fp.GetReference()=='C2':
   fp.Models().clear();m=pcb.FP_3DMODEL();m.m_Filename='${KIPRJMOD}/models/GRM219R61E106KA12D_max_with_solder.step';fp.Models().push_back(m)
   dst=dest/'models/GRM219R61E106KA12D_max_with_solder.step';dst.parent.mkdir(exist_ok=True);shutil.copy2(ROOT/'generated/revM/electronic_envelopes'/dst.name,dst)
   continue
  for model in fp.Models():
   path=model.m_Filename.replace('${KICAD10_3DMODEL_DIR}',str(LIB/'3dmodels')).replace('${KIPRJMOD}',str(source));src=Path(path)
   if not src.exists():missing.append(dict(ref=fp.GetReference(),model=model.m_Filename));continue
   short=src.parent.name.replace('.3dshapes','')+'__'+src.name;dst=dest/'models'/short;dst.parent.mkdir(exist_ok=True);shutil.copy2(src,dst);model.m_Filename='${KIPRJMOD}/models/'+short
 (dest/'fp-lib-table').write_text('(fp_lib_table '+''.join(f'(lib (name "{lib}") (type "KiCad") (uri "${{KIPRJMOD}}/footprints/{lib}.pretty") (options "") (descr "Pinned footprint"))' for lib in sorted(fplibs))+')',encoding='utf-8')
 pcb.SaveBoard(str(dest/(name+'.kicad_pcb')),board)
 fab=dest/'fabrication_candidate';fab.mkdir(exist_ok=True)
 run(['sch','erc','--format','json','--exit-code-violations','-o',dest/'erc.json',dest/(name+'.kicad_sch')])
 run(['pcb','drc','--schematic-parity','--format','json','--exit-code-violations','-o',dest/'drc.json',dest/(name+'.kicad_pcb')])
 layers='F.Cu,In1.Cu,In2.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts' if kind=='regional_revM' else 'F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts'
 run(['pcb','export','gerbers','-l',layers,'-o',str(fab)+'/',dest/(name+'.kicad_pcb')]);run(['pcb','export','drill','-o',str(fab)+'/',dest/(name+'.kicad_pcb')])
 run(['pcb','export','pos','--format','csv','--units','mm','--use-drill-file-origin','--smd-only','-o',dest/'placement.csv',dest/(name+'.kicad_pcb')])
 # Component bounds used by the mechanical assembly supplement any missing vendor models.
 run(['pcb','export','step','--subst-models','--drill-origin','-f','-o',dest/'board_native.step',dest/(name+'.kicad_pcb')])
 bom=[]
 for fp in board.GetFootprints():
  if fp.GetAttributes()&pcb.FP_EXCLUDE_FROM_BOM:continue
  bom.append(dict(reference=fp.GetReference(),value=fp.GetValue(),footprint=str(fp.GetFPID().GetLibNickname())+':'+str(fp.GetFPID().GetLibItemName()),side='B' if fp.IsFlipped() else 'F',x_mm=pcb.ToMM(fp.GetPosition().x),y_mm=pcb.ToMM(fp.GetPosition().y),rotation_deg=fp.GetOrientationDegrees()))
 (dest/'bom.json').write_text(json.dumps(bom,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 record=dict(kind=kind,pcb_sha256=hashlib.sha256((dest/(name+'.kicad_pcb')).read_bytes()).hexdigest(),schematic_sha256=hashlib.sha256((dest/(name+'.kicad_sch')).read_bytes()).hexdigest(),erc_pass=True,drc_parity_pass=True,missing_vendor_3D_models=missing,manufacturing_released=False,hardware_tested=False)
 (dest/'validation.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');print(kind,'ERC / DRC / parity PASS; missing vendor models',len(missing),flush=True)
 return record
if __name__=='__main__':
 results=[]
 for k,n in NAMES.items():results.append(package(k,n))
 (ROOT/'verification/revM_electronics_package.json').write_text(json.dumps(results,indent=2)+'\n',encoding='utf-8')
