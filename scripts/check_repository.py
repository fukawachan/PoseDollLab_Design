"""Validate the standalone source/input layout; optionally check local exports and a C golden frame."""
import argparse, hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
HW=ROOT/'Hardware/PoseDoll44'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--local-exports',action='store_true');ap.add_argument('--golden',type=Path);a=ap.parse_args()
 checked={}
 for character in ('manny','quinn'):
  for rev in ('revM','revN'):
   p=HW/f'generated/{rev}/{character}/manufacturing_manifest.json';m=json.loads(p.read_text(encoding='utf-8'))
   for rel,expected in m['source_sha256'].items():
    p=HW/rel.replace('\\','/');assert p.is_file(),f'Missing design input: {p}'
    if p not in checked:checked[p]=sha(p)
    assert checked[p]==expected,f'Changed historical geometry input: {p}'
   if a.local_exports:
    for part in m['parts']:
     assert (HW/f'generated/{rev}/{character}'/part['STEP']).is_file(),part['STEP']
  if a.local_exports:
   assert (HW/f'generated/revN/{character}/meshes.bin').stat().st_size>0
 snapshot=json.loads((ROOT/'docs/software_snapshot.json').read_text(encoding='utf-8'))
 for entry in snapshot['files']:
  p=ROOT/entry['path'];assert p.is_file() and sha(p)==entry['sha256'],f'Changed compatibility snapshot: {p}'
 table=(HW/'electronics/sensor_revC_mini/fp-lib-table').read_text(encoding='utf-8')
 assert '${KIPRJMOD}/PoseDoll.pretty' in table and 'DollSimulation/' not in table
 if a.golden:
  sys.path.insert(0,str(ROOT/'Tools/PoseDollHardwareBridge'))
  from pd41_protocol import encode_diagnostic,decode,FIXED
  actual=a.golden.read_bytes();expected=encode_diagnostic(words=[FIXED]*3+[555]*41,timings=[[0,2000]]*6,device=0x123456789abc,boot=789,sequence=1,timestamp_us=1000,window_us=2000,presence=63)
  assert actual==expected and decode(actual[:-1])['pose_valid'],'C/Python framing mismatch'
 print(json.dumps({'status':'PASS','geometry_inputs_checked':len(checked),'compatibility_files_checked':len(snapshot['files']),'local_exports_checked':a.local_exports,'C_Python_golden_match':bool(a.golden)},indent=2))
if __name__=='__main__':main()
