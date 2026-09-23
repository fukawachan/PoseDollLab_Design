"""Derive manufacturing routes and calibration worksheets from the delivered model."""
from pathlib import Path
import json,csv,re,collections,hashlib,math
ROOT=Path(__file__).resolve().parents[1]
def save(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def classify(p):
 n,m,note=p['id'],p['material'],p['note']
 if m in ('pcb','pcb_component') or p['role']=='purchased_assembly':return 'PCBA内含','按电子板成套，不按机械实体重复采购'
 if 'print' in p:return '打印','PLA 候选，按随件 STL 和切片复核要求'
 if m=='magnet':return '采购标准件','AS5000-MD6H-2 候选，Ø6×2.5 径向充磁，逐件核对磁场'
 if 'disc_spring' in n or ('_G4_' in n and 'disc_' in n):return '采购碟簧','按弹簧型号和装配方向，不按 CAD 色彩选型'
 if m in ('ptfe_composite','thrust'):return '采购标准件','SKF PCMW 102001.5 E；以当前 STEP 尺寸核对'
 if re.search(r'M\d+(?:x\d+)?',n) and not any(x in n.lower() for x in ('frame','carrier','plate','socket','bush','support','keeper','cap','lining','shell','magnet_cup','spring','washer','spacer','clip','rail','cleat','post','pod')):
  return '采购紧固件','按螺纹、长度、材料和实际头部包络一起核对'
 if re.search(r'M\d+x\d+',n) and ('set_' in n or '_M' in n):return '采购紧固件','按螺纹、长度、材料和实际头部包络一起核对'
 if p['material']=='nylon' and 'strap' in n:return '采购辅件','PA66 2.5 mm 宽扎带；按装配长度修整'
 if m=='silicone':return '模切软垫','硅胶片；CAD 安装厚度，见自由厚度说明'
 if m in ('pom','peek','nylon'):return '加工塑料','POM-C / 未填充 PEEK / PA12 按材质分别加工；薄件不等同 PLA 打印'
 return '加工金属','按 STEP 加工并检验配合；复杂框架先反馈 DFM'
def spring_pn(n,note):
 if '_G4_' in n:return 'SCHNORR 001800'
 if '_clutch_disc_spring_' in n:return 'SCHNORR 002200'
 found=re.search(r'SCHNORR\s+(\d{3})\s*(\d{3})',note)
 return 'SCHNORR '+''.join(found.groups()) if found else ''
def main():
 out={}
 for name in ('manny','quinn'):
  folder=ROOT/f'generated/revM/{name}';mf=folder/'manufacturing_manifest.json';d=json.loads(mf.read_text());rows=[];summary=collections.Counter();stock=collections.defaultdict(list)
  for p in d['parts']:
   cat,action=classify(p);summary[cat]+=1;n=p['id'];size=re.search(r'M(\d+(?:\.\d+)?)(?:x(\d+(?:\.\d+)?))?',n);thread=('M'+size[1]) if size else '';length=(size[2] or '') if size else '';pn='';info=(n+' '+p['note']).lower();style=('hex_nut' if 'nut' in info else 'set_screw' if ('set_' in n or 'set screw' in info) else 'button_head' if ('button' in info or p['material']=='titanium') else 'screw_head_to_drawing') if cat=='采购紧固件' else '';bounds=p['local_bounds_mm'];envelope=tuple(round(v,3) for v in sorted(bounds[i+3]-bounds[i] for i in range(3)))
   if cat=='采购碟簧':pn=spring_pn(n,p['note']);assert pn,n
   elif p['material']=='magnet':pn='AS5000-MD6H-2'
   elif p['material'] in ('ptfe_composite','thrust'):pn='PCMW 102001.5 E'
   elif p['material']=='titanium':pn='SSB-M3-8-TI5'
   row=dict(part_id=n,owner=p['owner'],category=cat,material=p['material'],quantity=1,candidate_part_number=pn,thread=thread,length_mm=length,fastener_form=style,CAD_envelope_mm=' x '.join(str(v) for v in envelope),action=action,STEP=p['STEP'],STL=p.get('print',{}).get('STL',''),note=p['note']);rows.append(row)
   if cat.startswith('采购'):stock[(cat,pn,thread,length,p['material'],style,envelope if cat=='采购紧固件' else ())].append(n)
  with (folder/'procurement_routes.csv').open('w',newline='',encoding='utf-8-sig') as f:
   w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
  save(folder/'procurement_routes.json',dict(source_manifest_sha256=hashlib.sha256(mf.read_bytes()).hexdigest(),classification_counts=dict(summary),rows=rows,not_purchase_authorization=True))
  groups=[dict(category=k[0],candidate_part_number=k[1],thread=k[2],length_mm=k[3],material=k[4],fastener_form=k[5],CAD_envelope_mm=list(k[6]),quantity=len(v),instances=v,head_and_geometry_check_required=True) for k,v in stock.items()]
  save(folder/'stock_quantity_summary.json',groups)
  p=d['profile'];cal=[]
  for axis in p['axes']:
   a=axis['id']
   if a.startswith('pelvis.'):continue
   lo,hi=[math.degrees(v) for v in axis['limits_rad']];start=max(-40,lo);end=min(40,hi);assert end-start>=20-1e-6,a
   points=[round(start,3),round((start+end)/2,3),round(end,3)]
   for i,v in enumerate(points):cal.append(dict(axis_id=a,reference_index=i+1,known_joint_deg=v,raw_capture_file='',observed_raw_count='',status='未测',fixture_requirement='固定其他轴；相对该机械轴固定侧测角；量角不确定度目标≤0.5°'))
  with (folder/'calibration_reference_plan.csv').open('w',newline='',encoding='utf-8-sig') as f:
   w=csv.DictWriter(f,fieldnames=list(cal[0]));w.writeheader();w.writerows(cal)
  out[name]=dict(entities=len(rows),categories=dict(summary),individual_calibration_observations=len(cal),PCBA_order=dict(sensor_small=39,sensor_large=2,regional=6,power=1))
 save(ROOT/'verification/revM_procurement_summary.json',out);print(json.dumps(out,ensure_ascii=False))
if __name__=='__main__':main()
