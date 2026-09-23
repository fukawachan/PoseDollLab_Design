"""Calibrate PD41 captured data; no serial/UE connection, no invented hardware zeros."""
from pathlib import Path
import argparse,datetime,hashlib,json,math,statistics,sys,uuid
from pd41_protocol import CFG
from full_diagnose import analyze
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'Tools/PoseDollSimulator/src'))
from posedoll_sim.core import DeviceProfile
TAU=2*math.pi

def wrap(x):return (x+math.pi)%TAU-math.pi

def profile_data(character):
 p=ROOT/f'Hardware/PoseDoll44/mechanical_manifest/interfaces_revM_{character}.json'
 d=json.loads(p.read_text(encoding='utf-8'))['profile']
 d['profile_id']=f'physical_{character}_41_revM';d['status']='physical_geometry_candidate_pelvis_fixed'
 d['notes_zh']=['骨盆三轴是显式固定参考；整体平移、航向、俯仰和侧倾均在 UE Placement 调整。','41 个相对转轴；尺寸来自当前 Rev M 总装；这不是传感器零点文件。']
 return d

def observe(character,axis,known_deg,capture_path):
 p=profile_data(character);limits={a['id']:a['limits_rad'] for a in p['axes']}
 if axis not in CFG['protocol_order'][3:]:raise ValueError('Choose one of the 41 measured axes')
 lo,hi=limits[axis];q=math.radians(known_deg)
 if not math.isfinite(q) or not lo<=q<=hi:raise ValueError('Reference angle outside mechanical profile')
 raw,frames,report=analyze(capture_path)
 if report['framing_or_session_errors'] or report['sequence_gaps'] or report['trailing_partial_frame_bytes']:raise ValueError('Capture contains transport/session errors')
 i=CFG['protocol_order'].index(axis)
 if len(frames)<30 or any(f['axes'][i]['status']!='valid' for f in frames):raise ValueError('At least 30 continuous valid stationary samples required for this axis')
 radians=[f['axes'][i]['count']*TAU/16384 for f in frames];mean=math.atan2(sum(math.sin(x) for x in radians),sum(math.cos(x) for x in radians))%TAU
 residuals=[wrap(x-mean) for x in radians];spread=max(residuals)-min(residuals)
 if spread>math.radians(.4):raise ValueError('More than 0.4 degree raw spread: hold still and inspect the sensor')
 return dict(axis_id=axis,known_joint_rad=q,mean_raw_rad=mean,spread_deg=math.degrees(spread),samples=len(frames),device_id=frames[0]['device_id'],character=character,source_capture_sha256=hashlib.sha256(raw).hexdigest(),source_capture=str(Path(capture_path).resolve()),recorded_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())

def fit_axis(axis,observations):
 rows=[r for r in observations if r['axis_id']==axis]
 q=[r['known_joint_rad'] for r in rows]
 if len(rows)<3 or len({round(x,5) for x in q})<3 or max(q)-min(q)<math.radians(20)-1e-8:raise ValueError(axis+': three distinct known angles spanning at least 20 degrees are required')
 if max(q)-min(q)>math.radians(160):raise ValueError(axis+': use a calibration span no larger than 160 degrees')
 candidates=[]
 for sign in (-1,1):
  offsets=[r['mean_raw_rad']-sign*r['known_joint_rad'] for r in rows];zero=math.atan2(sum(math.sin(x) for x in offsets),sum(math.cos(x) for x in offsets))%TAU
  errors=[math.degrees(wrap(r['mean_raw_rad']-zero-sign*r['known_joint_rad'])) for r in rows]
  candidates.append((max(abs(x) for x in errors),sign,zero,errors))
 error,sign,zero,errors=min(candidates)
 if error>1.0:raise ValueError(axis+': reference check exceeds 1 degree; do not fit away nonlinear or mounting errors')
 return dict(axis_id=axis,zero_raw_rad=zero,sign=sign,joint_rad_per_sensor_rad=1.0,raw_period_rad=TAU),dict(axis_id=axis,maximum_reference_error_deg=error,errors_deg=errors,observations=len(rows))

def build_bundle(character,observations,assembly_id,dest):
 dest=Path(dest)
 if dest.exists():raise ValueError('Output must be a new directory; no active profile is overwritten')
 if not assembly_id.strip() or len(assembly_id)>64:raise ValueError('Enter an assembly label of 1..64 characters')
 p=profile_data(character);ids=CFG['protocol_order'];measured=ids[3:]
 if set(r['axis_id'] for r in observations)!=set(measured):raise ValueError('All 41 measured axes must have observations')
 limits={a['id']:a['limits_rad'] for a in p['axes']}
 for row in observations:
  lo,hi=limits[row['axis_id']]
  for field in ('known_joint_rad','mean_raw_rad','spread_deg'):
   if type(row.get(field)) not in (int,float) or not math.isfinite(row[field]):raise ValueError('Non-finite or missing observation field: '+field)
  if not lo<=row['known_joint_rad']<=hi or not 0<=row['mean_raw_rad']<TAU or not 0<=row['spread_deg']<=.4 or type(row.get('samples')) is not int or row['samples']<30:raise ValueError('Observation limits, range, stability, or sample count failed')
 identities={r['device_id'] for r in observations}
 if len(identities)!=1 or any(r['character']!=character for r in observations):raise ValueError('Mixed devices or character profiles')
 axes=[dict(axis_id=a,zero_raw_rad=0,sign=1,joint_rad_per_sensor_rad=1.0,raw_period_rad=TAU,fixed_reference_unused=True) for a in ids[:3]];checks=[]
 for a in measured:
  c,check=fit_axis(a,observations);axes.append(c);checks.append(check)
 pb=(json.dumps(p,ensure_ascii=False,indent=2)+'\n').encode('utf-8');ph=hashlib.sha256(pb).hexdigest()
 calibration=dict(schema_version='1.0',calibration_id='pd41-'+str(uuid.uuid4()),profile_id=p['profile_id'],profile_sha256=ph,status='bench_zero_direction_checked',device_id=next(iter(identities)),assembly_id=assembly_id,axes=axes,reference_checks=checks,physical_load_or_flex_qualified=False)
 cap=dict(schema_version='1.0',capability_id=f'physical_{character}_41_pelvis_fixed_revM',profile_id=p['profile_id'],measured_axis_ids=measured,fixed_axis_values_rad={a:0 for a in ids[:3]})
 folder=dest/'Profiles';folder.mkdir(parents=True)
 (folder/'virtual_humanoid_44_v1.json').write_bytes(pb)
 for name,obj in [('virtual_zero_pi_v1.json',calibration),('body35_capabilities.json',cap)]:
  (folder/name).write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 (dest/'observations.json').write_text(json.dumps(observations,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
 DeviceProfile(dest) # Validate against the same Python schema used by the simulator.
 return calibration

def main():
 ap=argparse.ArgumentParser(description=__doc__);sub=ap.add_subparsers(dest='command',required=True)
 p=sub.add_parser('observe');p.add_argument('--character',choices=['manny','quinn'],required=True);p.add_argument('--axis',required=True);p.add_argument('--angle-deg',type=float,required=True);p.add_argument('--input',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
 p=sub.add_parser('build');p.add_argument('--character',choices=['manny','quinn'],required=True);p.add_argument('--observations',type=Path,nargs='+',required=True);p.add_argument('--assembly-id',required=True);p.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 if a.command=='observe':
  row=observe(a.character,a.axis,a.angle_deg,a.input)
  with a.out.open('x',encoding='utf-8') as f:json.dump(row,f,ensure_ascii=False,indent=2)
  print(json.dumps(row,ensure_ascii=False))
 else:
  rows=[]
  for path in a.observations:
   v=json.loads(path.read_text(encoding='utf-8'));rows.extend(v if isinstance(v,list) else [v])
  cal=build_bundle(a.character,rows,a.assembly_id,a.out);print('Calibration bundle:',a.out,';',cal['calibration_id'])
if __name__=='__main__':main()
