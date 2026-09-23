"""Read-only dimensional audit against the project's captured Manny reference.
Does not alter the simulator, UE assets, profiles, or Rev C CAD evidence.
"""
from pathlib import Path
import json,math,hashlib
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def read(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def neutral_origins(profile):
 out={}
 for n in profile['nodes']:
  base=out[n['parent']] if n['parent'] else [0.,0.,0.]
  for key in ('parent_to_axis','axis_to_child'):
   if n[key]['rotation_xyzw']!=[0,0,0,1]:raise ValueError('Nonidentity reference rotation requires full FK: '+n['id'])
  out[n['id']]=[base[i]+1000*(n['parent_to_axis']['translation_m'][i]+n['axis_to_child']['translation_m'][i]) for i in range(3)]
 return out

def main():
 target_path=REPO/'Shared/Profiles/manny_body_ue582_v1.json'
 reference_path=REPO/'reports/rig_runtime_probe.json'
 fixture_path=REPO/'reports/rig_fixture_results.json'
 body_path=ROOT/'mechanical_manifest/physical_humanoid_44_revC_design.json'
 target=read(target_path);ref=read(reference_path);fixture=read(fixture_path);body=read(body_path)
 if fixture['rig_runtime_sha256']!=target['rig_runtime_sha256']:raise ValueError('Cached fixture fingerprint does not match target profile')
 bones={x['name']:x['global']['translation'] for x in ref['mesh_reference']}
 hardware=neutral_origins(body)
 axis_nodes={a['id']:a['node'] for a in body['axes']}
 def dist(points,a,b):return math.dist(points[a],points[b])
 rows=[];ratios={}
 for side in ('l','r'):
  segments=[('upper_arm',f'upperarm_{side}',f'lowerarm_{side}',f'upperarm_{side}.abduct_frame',axis_nodes[f'elbow_{side}.flex']),
   ('forearm',f'lowerarm_{side}',f'hand_{side}',axis_nodes[f'elbow_{side}.flex'],f'hand_{side}.flex_frame'),
   ('thigh',f'thigh_{side}',f'calf_{side}',f'thigh_{side}.flex_frame',axis_nodes[f'calf_{side}.flex']),
   ('shin',f'calf_{side}',f'foot_{side}',axis_nodes[f'calf_{side}.flex'],f'foot_{side}.dorsiflex_frame')]
  # Match total hip-knee-ankle chain only as a comparison baseline, not a final body scale.
  target_leg=10*(dist(bones,f'thigh_{side}',f'calf_{side}')+dist(bones,f'calf_{side}',f'foot_{side}'))
  actual_leg=dist(hardware,f'thigh_{side}.flex_frame',axis_nodes[f'calf_{side}.flex'])+dist(hardware,axis_nodes[f'calf_{side}.flex'],f'foot_{side}.dorsiflex_frame')
  scale=actual_leg/target_leg
  values={}
  for name,ta,tb,ha,hb in segments:
   t=dist(bones,ta,tb)*10;h=dist(hardware,ha,hb);expected=t*scale
   values[name]=(t,h)
   rows.append(dict(side=side,segment=name,target_bone_start=ta,target_bone_end=tb,hardware_start=ha,hardware_end=hb,target_mm=t,current_revC_mm=h,comparison_scale=scale,equivalent_target_at_current_leg_length_mm=expected,deviation_percent=100*(h/expected-1)))
  ta=values['upper_arm'][0]+values['forearm'][0];ha=values['upper_arm'][1]+values['forearm'][1]
  ratios[side]={'manny_arm_chain_divided_by_leg_chain':ta/target_leg,'revC_arm_chain_divided_by_leg_chain':ha/actual_leg,
   'arm_ratio_excess_percent':100*((ha/actual_leg)/(ta/target_leg)-1),
   'shoulder_flex_abduct_axis_separation_mm':dist(hardware,f'upperarm_{side}.flex_frame',f'upperarm_{side}.abduct_frame'),
   'shoulder_abduct_twist_axis_origin_separation_mm':dist(hardware,f'upperarm_{side}.abduct_frame',f'upperarm_{side}')}
 widths={
  'manny_shoulder_joint_centres_mm':dist(bones,'upperarm_l','upperarm_r')*10,
  'revC_shoulder_flex_axes_mm':dist(hardware,'upperarm_l.flex_frame','upperarm_r.flex_frame'),
  'revC_shoulder_abduct_axes_mm':dist(hardware,'upperarm_l.abduct_frame','upperarm_r.abduct_frame'),
  'manny_hip_joint_centres_mm':dist(bones,'thigh_l','thigh_r')*10,
  'revC_hip_flex_axes_mm':dist(hardware,'thigh_l.flex_frame','thigh_r.flex_frame')}
 data={'status':'FAIL_REVC_NOT_PROPORTION_MATCHED','target_mesh':target['mesh'],'target_rig':target['rig'],
  'source_basis':'Existing project mesh-reference capture; cached validated target, not a fresh current-editor interrogation.',
  'target_fingerprint_matches_fixture':True,'target_rig_fingerprint':target['rig_runtime_sha256'],
  'whole_mesh_height_mm':None,'physical_whole_height_mm':None,'height_note':'head_tip Z=550mm is a CAD reference coordinate, not sole-to-crown stature. No arm/height claim is made without actual mesh surface bounds.',
  'rows':rows,'ratios':ratios,'widths':widths,'sources_sha256':{str(p.relative_to(REPO)):sha(p) for p in (target_path,reference_path,fixture_path,body_path)},
  'limitations':['Arm chain means shoulder abduction centre -> elbow -> wrist; excludes hand and fingers.','Leg chain means hip flexion centre -> knee -> ankle; excludes foot.','Separate shoulder pivots cannot be represented by a single anatomical shoulder centre; quoted arm-chain lengths alone do not qualify this mechanism.','Matching link lengths alone cannot prove endpoint equivalence; torso motion distribution and joint centre trajectories must also be checked.','No new user measurements are required.']}
 out=ROOT/'verification/proportion_audit_revC_vs_manny.json';out.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
 report=['# Manny 体格比例核对','', '**结论：当前 Rev C 布局不满足等比例要求，不能据此固定全身尺寸。**','',
 '目标为项目已验证的 `SKM_Manny_Simple` / `CR_Mannequin_Body`。尺寸取自此前 UE 导出的真实网格参考骨架；已有测试的 Rig 指纹与目标配置一致。本次没有改动 UE 资产或模拟器，也没有重新读取当前编辑器资产。','',
 '下表以左腿“髋—膝—踝”总长 235 mm 为统一比较基准，将 Manny 等比缩小。它用于暴露偏差，不是已经选定的最终身高。','',
 '| 测量段（关节中心之间） | 当前 Rev C | 按 Manny 比例应为 | 偏差 |','|---|---:|---:|---:|']
 labels={'upper_arm':'上臂：肩外展轴—肘','forearm':'前臂：肘—腕','thigh':'大腿：髋—膝','shin':'小腿：膝—踝'}
 for r in rows:
  if r['side']=='l':report.append(f"| {labels[r['segment']]} | {r['current_revC_mm']:.1f} mm | {r['equivalent_target_at_current_leg_length_mm']:.1f} mm | {r['deviation_percent']:+.1f}% |")
 ratio=ratios['l']
 report+=['',f"两节手臂 / 两节腿长：Manny 为 **{ratio['manny_arm_chain_divided_by_leg_chain']:.3f}**，Rev C 为 **{ratio['revC_arm_chain_divided_by_leg_chain']:.3f}**。这项比例已经明显不同，与整机最终缩放为多高无关。",'',
 '当前肩屈伸轴与外展轴还相距 56 mm，因此不存在一个与 Manny 对应的共同肩关节中心。这会造成随姿势变化的位置差，不能仅缩短两根连杆就宣称解决。','',
 '现有 UE 适配层主要采用源肢体朝向，并保留目标 Manny 自己的骨长；角度映射通过不等于身体比例或手脚接触通过。尤其双手合拢、抱臂、扶额、叉腰、跪坐需要单独的空间误差检查。','',
 '## 修订后的设计约束','',
 '1. 以同一份 Manny 参考数据生成机械关节目标坐标和比例报告，所有主要尺寸使用同一个缩放系数。','2. 同时约束上臂、前臂、大腿、小腿、肩宽、髋宽、骨盆至肩的高度，以及头、手、脚的外形参考。','3. 关节中心及转动轨迹优先；电子板、摩擦模块和外壳围绕这些位置布置。需要空间时优先增大全身统一比例或改机构，不能单独拉长胳膊、扩大肩宽。','4. 机械多轴中心偏移和简化躯干轴的影响必须进入 FK 比较；在统一根坐标、等比例和相同输入下，核对腕、踝、头及接触点。','5. 全身外形高度以脚底到头顶定义，支架、外伸传感器和旧 head_tip 的绝对 Z 坐标不作为身高。','6. 现有单关节模块保留为结构研究件，全身安装位置与尺寸等待这项比例检查通过。无需用户先行打印或测量。','',
 '数字目标见 [比例约束](../mechanical_manifest/proportion_constraints_revD.json)。它们是新设定的设计验收目标，尚未达到，不是制造误差或人体标准。','',
 '[机器可读结果](proportion_audit_revC_vs_manny.json) · [检查脚本](../tools/audit_proportions.py)','']
 (ROOT/'verification/PROPORTION_AUDIT.zh-CN.md').write_text('\n'.join(report),encoding='utf8')
 print(json.dumps({'status':data['status'],'ratios':ratios,'rows_left':rows[:4]},ensure_ascii=False))
if __name__=='__main__':main()
