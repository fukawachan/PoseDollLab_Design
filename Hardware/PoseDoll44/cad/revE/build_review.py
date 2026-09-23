from character_reference import *

def main():
 baseline=json.loads((ROOT/'verification/revE_proportion_baselines.json').read_text(encoding='utf8'))
 data={'characters':{},'measurements':{k:v['measurements_mm'] for k,v in baseline['characters'].items()}}
 for name in ('manny','quinn'):
  d=json.loads((OUT/name/'viewer_data.json').read_text(encoding='utf8'))
  p=json.loads((ROOT/'mechanical_manifest'/('physical_'+name+'_44_revE_proportion.json')).read_text(encoding='utf8'));T,_=fk(p,{})
  d['links']=[[T[n['parent']][:3,3].tolist(),T[n['id']][:3,3].tolist()] for n in p['nodes'] if n['parent'] is not None and n['parent']!='device_base' and np.linalg.norm(T[n['id']][:3,3]-T[n['parent']][:3,3])>.001]
  data['characters'][name]=d
 template=(HERE/'review.template.html').read_text(encoding='utf-8-sig')
 (OUT/'Manny_Quinn_3D_Review.html').write_text(template.replace('__POSEDOLL_DATA__',json.dumps(data,separators=(',',':'))),encoding='utf8')
 print(json.dumps({'viewer':'generated/revE/Manny_Quinn_3D_Review.html','axes':{n:len(d['joints']) for n,d in data['characters'].items()}}))
if __name__=='__main__':main()
