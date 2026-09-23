"""Finalize a hash-indexed digital prototype only after all current checks pass."""
from pathlib import Path
import json,hashlib,datetime,re,math
R=Path(__file__).resolve().parents[1];REPO=R.parents[1]
NAMES=('manny','quinn')
def read(rel):return json.loads((R/rel).read_text(encoding='utf-8'))
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1048576),b''):h.update(b)
 return h.hexdigest()
def check_sources(d,root=R):
 for rel,h in d.items():assert sha(root/rel)==h,('stale input',rel)
def write(rel,d):(R/rel).write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
 audit=read('verification/revM_complete_audit.json');loads=read('verification/revM_load_work.json');access=read('verification/revM_cover_assembly_access.json');proportion=read('verification/revM_proportions.json');elect=read('verification/revM_electronics_package.json');fw=read('verification/revM_firmware_package.json');offline=read('verification/revM_offline_tests.json');browser=read('verification/browser_revM/checks.json');proc=read('verification/revM_procurement_summary.json');strength=read('verification/revM_strength_handling_screen.json');mapping=read('verification/revM_kinematic_mapping.json');printmesh=read('verification/revM_print_mesh_export.json');printcheck=read('verification/revM_print_exports.json');printclear=read('verification/revM_print_process_clearance.json')
 assert offline['passed'] and offline['failures']==offline['errors']==0 and offline['C_Python_golden_match']
 check_sources(offline['source_sha256'],REPO);check_sources(fw['source_sha256'],REPO);check_sources(browser['source_sha256']);assert not browser['errors']
 assert strength['source_load_sha256']==sha(R/'verification/revM_load_work.json')
 assert len(elect)==4 and len(fw['nodes'])==6
 for e in elect:
  folder=R/'generated/revM/electronics'/e['kind'];pcb=list(folder.glob('*.kicad_pcb'));sch=list(folder.glob('*.kicad_sch'));assert len(pcb)==len(sch)==1
  assert sha(pcb[0])==e['pcb_sha256'] and sha(sch[0])==e['schematic_sha256'] and e['erc_pass'] and e['drc_parity_pass']
 for n in fw['nodes']:
  for im in n['images']:assert sha(R/f'generated/revM/firmware/node{n["node"]}'/im['file'])==im['sha256']
 characters={}
 for name in NAMES:
  base=f'generated/revM/{name}';mf=read(base+'/manufacturing_manifest.json');viewer=read(base+'/viewer.json');interfaces=read(f'mechanical_manifest/interfaces_revM_{name}.json');harness=read(f'harness/{name}_revM.json');power=read(f'verification/revM_harness_power_{name}.json');a=audit['characters'][name];b=loads[name];src=mf['source_sha256'];check_sources(src)
  check_sources(mapping['characters'][name]['source_sha256'],REPO)
  assert mapping['characters'][name]['samples']==635
  for d,key in [(mapping['characters'][name],'source_cad_sha256'),(a,'source_sha256'),(viewer,'source_sha256'),(interfaces,'source_sha256'),(access[name],'source_sha256'),(harness,'source_cad_sha256'),(b,'source_cad_sha256'),(proportion['characters'][name],'source_cad_sha256')]:assert d[key]==src,(name,key)
  check_sources(harness['source_sha256']);hh=sha(R/f'harness/{name}_revM.json');assert power['source_harness_sha256']==b['source_harness_sha256']==hh
  assert printcheck[name]['passed'] and printcheck[name]['count']==187
  assert printcheck[name]['source_manifest_sha256']==sha(R/base/'manufacturing_manifest.json')
  assert printclear[name]['passed'] and len(printclear[name]['checks'])==164
  assert printclear[name]['source_print_export_sha256']==b['source_print_export_sha256']==sha(R/'verification/revM_print_mesh_export.json')
  assert printclear[name]['source_cad_sha256']==printmesh[name]['source_cad_sha256']==src
  print_checks={p['id']:p for p in printcheck[name]['checks']}
  changed_checks={p['part']:p for p in printclear[name]['changed_parts']}
  assert len(print_checks)==len(printmesh[name]['prints'])==187
  assert set(changed_checks)=={p['id'] for p in printmesh[name]['prints'] if p['print_process_STEP']}
  for pr in printmesh[name]['prints']:
   nominal=next(p for p in mf['parts'] if p['id']==pr['id']);assert pr['source_STEP_sha256']==sha(R/base/nominal['STEP'])
   assert pr['STL_sha256']==print_checks[pr['id']]['sha256']==sha(R/base/nominal['print']['STL'])
   if pr['print_process_STEP']:
    assert pr['STEP_readback_validated']
    assert sha(R/base/pr['print_process_STEP'])==pr['print_process_STEP_sha256']==changed_checks[pr['id']]['STEP_sha256']
    assert pr['STL_sha256']==changed_checks[pr['id']]['STL_sha256']
  assert power['reach_pass'] and b['pose_count']==191 and len(b['axes'])==41
  assert access[name]['passed'] and len(access[name]['checks'])==18
  assert len(mf['parts'])==a['parts']==len(viewer['parts'])==1999
  assert len(a['checks'])==len(viewer['poses'])==164 and a['structural_failed_poses']==0
  assert len(a['independent_cache_checks'])==3 and not a['excluded_out_of_profile_poses']
  for pose in a['checks']:
   assert pose['pose'] in viewer['poses'] and pose['angles_deg']==viewer['poses'][pose['pose']]['angles_deg']
   assert not any(h['classification']=='structural' for h in pose['review'])
  assert len(a['readout']['installations'])==len(a['endpoints'])==len(interfaces['channels'])==41 and len(a['readout']['pose_checks'])==164*41
  for endpoint in a['endpoints']:
   for c in endpoint['checks']:
    outside=c.get('outside',c.get('outside_allowed_range'))
    assert c['volume_mm3']>.02 if outside else c['volume_mm3']<=.02,(name,endpoint['axis'],c)
  capabilities=read(f'mechanical_manifest/physical_{name}_41_capabilities.json');assert capabilities['profile_id']==mf['profile']['profile_id'] and len(capabilities['measured_axis_ids'])==41 and len(capabilities['fixed_axis_values_rad'])==3
  assert len(harness['cables'])==52 and harness['termination_nodes']==[6,4] and harness['CAN_linear_order']==[6,1,5,3,2,4]
  assert read(base+'/procurement_routes.json')['source_manifest_sha256']==sha(R/base/'manufacturing_manifest.json')
  assert proportion['characters'][name]['source_manifest_sha256']==sha(R/base/'manufacturing_manifest.json') and proportion['characters'][name]['passed']
  prints=[p for p in mf['parts'] if 'print'in p];assert len(prints)==187 and all(p['print']['a1_mini_180_with_3mm_brim'] for p in prints)
  assert {p.stem for p in (R/base/'parts').glob('*.step')}=={p['id'] for p in mf['parts']}
  assert {p.stem for p in (R/base/'print_candidates').glob('*.stl')}=={p['id'] for p in prints}
  for p in mf['parts']:
   assert (R/base/p['STEP']).stat().st_size>0
   if 'print'in p:assert (R/base/p['print']['STL']).stat().st_size>0
  assert all(x['clutch_margin'] is not None and x['clutch_margin']>=1.5 for x in b['axes'])
  least=min(b['axes'],key=lambda x:x['clutch_margin']);warnings=[q['pose'] for q in a['checks'] if q['review']]
  characters[name]=dict(parts=1999,print_candidates=187,finite_pose_checks=164,structural_failed_poses=0,poses_with_nonadjacent_contacts=warnings,measured_axes=41,readout_pose_checks=6744,mechanical_limits_checked=41,arm_cover_access_checks=18,estimated_mass_kg=b['model_mass_kg']+b['allowance_mass_kg'],minimum_nominal_holding_ratio=least['clutch_margin'],minimum_holding_axis=least['axis'],reference_height_mm=proportion['characters'][name]['reference_surface_height_mm'],arm_height_ratio=proportion['characters'][name]['arm_to_reference_height_ratio'],harness_reach_comparisons=power['reach_comparisons'],nominal_input_A=power['nominal_design_envelope']['total_input_A'],minimum_node_input_V=power['nominal_design_envelope']['minimum_node_input_V'],mapping_head_error_mm=mapping['characters'][name]['worst_by_landmark']['head']['error_mm'],mapping_one_percent_target_met=mapping['characters'][name]['all_landmarks_within_one_percent'],source_cad_sha256=src)
 # Human-readable report is derived from the same checked files.
 lines=['# Rev M 完整数字原型验证报告','',f'生成时间：{datetime.datetime.now(datetime.timezone.utc).isoformat()}。状态：**完整数字原型候选，未制造放行、未实物鉴定**。','',
 '本次交付覆盖 Manny 与 Quinn 两款完整机械人偶。整体位置及全部整体旋转由 UE 手动调整；骨盆三槽为固定参考，其余 41 槽为测量。活动/形变部位裸露，稳定节段使用可拆刚性外壳。','',
 '## 两款整机结果','','| 项目 | Manny | Quinn |','|---|---:|---:|']
 table=[('人物参考高度（mm）','reference_height_mm',3),('左臂肩至指尖总长 / 参考身高','arm_height_ratio',6),('CAD 实体数量','parts',0),('打印候选 STL','print_candidates',0),('完整刚体离散姿态','finite_pose_checks',0),('发现相邻/内部结构交叠的姿态','structural_failed_poses',0),('41 轴测角几何复核次数','readout_pose_checks',0),('机械限位轴数','mechanical_limits_checked',0),('新增臂壳装配通道检查','arm_cover_access_checks',0),('含线束预留估重（kg）','estimated_mass_kg',3),('最小名义持姿 / 重力需求','minimum_nominal_holding_ratio',3),('线束跨度抽样比较次数','harness_reach_comparisons',0),('预算总输入电流（A）','nominal_input_A',3),('预算最低节点输入（V）','minimum_node_input_V',3)]
 for label,k,digits in table:lines.append('| '+label+' | '+' | '.join(f'{characters[n][k]:.{digits}f}' for n in NAMES)+' |')
 lines+=['','两款关节中心与已提取人物比例基线一致；这不代表外壳逐点复制角色皮肤，也不保证 Quinn 的软件绑定无需额外适配。最小持姿余量对应 '+', '.join(n+' / '+characters[n]['minimum_holding_axis'] for n in NAMES)+'。','',
 '颈部使用 neck_01、neck_02 与 head 参考位置的等效共心枢轴；它不是 UE 的 head 骨原点。635 个最终配置离线样本中，头部参考点最大轨迹差异为 Manny 14.32 mm、Quinn 16.52 mm，超出此前 1% 身高的参考目标；躯干分布式转动带来的上肢根部差异约 3.68 / 3.86 mm。结果没有标成全姿态位置一致。当前交付保留 41 轴机制，后续目标适配或 IK 应单独评估接触姿势，Quinn 预测也不等于 live Control Rig 已验证。','',
 '## 碰撞、限位与测角','','检查包含每轴端点/中点及全身组合动作，共每款 164 个离散姿态。体积超过 0.02 mm³ 的同体、同区域、相邻机构交叠计为结构问题；设计中的指定螺纹接触单独限定。每款 neutral、trunk_bend、arms_forward 三种姿态用不缓存的完整检查复核缓存结果。','',
 '保留的非相邻接触按用户确认的规则列为摆姿限制：Manny '+str(len(characters['manny']['poses_with_nonadjacent_contacts']))+' 个姿态，Quinn '+str(len(characters['quinn']['poses_with_nonadjacent_contacts']))+' 个姿态。查看器以橙色标出；原始接触对和体积没有删除。不能把“结构项通过”解释为这些动作可以直接穿过别的肢体。','',
 '41 轴均检查允许端点内无止挡交叠、越界 1° 出现止挡接触。实体芯片/磁铁面核对及刚体变换检查确认名义 1.5 mm 气隙与同轴关系；这不是磁场、14 位实际精度或实体零点校准。','',
 '仅新增的六组臂壳固定点验证了直线刀杆、螺钉头与螺母进入通道；按独立臂段先装壳的顺序。没有对全部紧固件做自动装配运动规划。整机碰撞是离散采样，不是连续全关节空间无碰撞证明。','',
 '## 持姿、强度与打印','','载荷计算检查 191 个相对姿态，对每姿态使用任意重力方向的轴向力矩上界。包含真实 CAD 零件质量估算、PCBA 质量分配及线束 15% 质量预留。PEEK 干摩擦系数 0.15、弹簧名义力均为待测假设；不包含线束恢复力、冲击、加速、磨损和 PLA 蠕变。','',
 '腰部名义持姿约 5.19 N·m，在 100 mm 有效力臂处理想操作力约 52 N。完整人偶约 3.2 kg，手感须与持姿能力一起验收。强度文件只列螺钉、螺纹、键面及梁的简化需求，没有执行 FEA、没有给出材料合格裕量或整机额定载荷。','',
 '187 个打印候选的名义包络均可进入 180 mm 打印空间并在 X/Y 保留 3 mm 裙边。Manny 右小腿梁最紧，含裙边约 179.55 mm。未实际切片；支撑足迹、层间强度、孔位和翘曲仍须首件验证。金属轴系、POM/PEEK、弹簧、PCBA 需要采购或加工。','',
 'STL 还经过逐件闭合边、尺寸与体积检查。每款有 6 个名义实体的相切边需要半径 0.10 mm 的小圆筋作为打印工艺修正，另附同名 `_print_process.step`。名义总装 STEP 保留设计基准，打印使用已经修正的 STL；全部修正件在同样 164 个姿态中检查了与整机其余部件的干涉，并回算质量与持姿需求。网格闭合仍不替代实际切片和强度验收。','',
 '## 电路、线束与数据','','四套 KiCad 工程的 ERC、DRC 和原理图/PCB 一致性为零违规。两种传感器板、区域板、电源板均有原生工程、Gerber/钻孔候选、BOM 与贴装坐标。区域/电源板原生 STEP 缺 5 / 1 个供应商模型，整机 CAD 用相应尺寸包络补充。USB 阻抗叠层、散热过孔工艺与代料要由制板方确认。','',
 '每款线束包含 41 条传感器、5 条 CAN 和 6 条电源线。164 个检查姿态加 1,000 个随机姿态独立验证端点距离不超过预留跨度；这只证明长度上界，不是弹性线束避碰、弯曲疲劳或信号完整性模拟。电源预算用 150 mA MCU 分配及 80% 效率等假设；200 mA 敏感性工况另列，不能当作已经满足全部余量。','',
 f'六个节点已在 ESP-IDF 6.1 构建并打包。离线验证：{offline["tests_run"]} 项 Python 测试、9 个 C 核心场景及 C/Python 黄金字节一致性通过。未烧录，未打开硬件端口，未采集实物数据。校准工具使用显式设备和角色绑定、至少三角度/轴；交付校准工单仍标为未测。','',
 'UE 插件与模拟器保留用户原先测试通过的状态。本轮只新增硬件诊断、实体校准流程及离线协议转换；正式实时桥接、Quinn 专属绑定和实体 Capture 仍需接入测试。','',
 '## 证据与执行入口','',
 '- [整机检查原始记录](revM_complete_audit.json) · [比例核对](revM_proportions.json) · [离线映射轨迹差异](revM_kinematic_mapping.json) · [装配通道](revM_cover_assembly_access.json)',
 '- [打印网格检查](revM_print_exports.json) · [工艺变体记录](revM_print_mesh_export.json) · [变体干涉复核](revM_print_process_clearance.json)',
 '- [重力/持姿预算](revM_load_work.json) · [强度与操作力需求](revM_strength_handling_screen.json)',
 '- [电路检查与哈希](revM_electronics_package.json) · [固件镜像记录](revM_firmware_package.json) · [离线测试](revM_offline_tests.json)',
 '- [Manny 线束/电源计算](revM_harness_power_manny.json) · [Quinn 线束/电源计算](revM_harness_power_quinn.json)',
 '- [查看器检查](browser_revM/checks.json) · [文件指纹清单](../generated/revM/delivery_manifest.json)',
 '- [完整交付入口](../START_HERE.zh-CN.md) · [装配手册](../docs/ASSEMBLY_REVM.zh-CN.md) · [分阶段实物验收](../docs/BUILD_AND_CALIBRATE_REVM.zh-CN.md)','',
 '先由加工方完成一套高负载关节和受力梁首件，再验证单板/最长线束、单肢与一款整机。当前无需一次制造两整套；上述待测项目都有验收入口，未填写为通过。','']
 (R/'verification/REVM_REPORT.zh-CN.md').write_text('\n'.join(lines),encoding='utf-8')
 files=set()
 def add(p):
  p=p.resolve();assert p.is_file(),str(p);files.add(p)
 def tree(p):
  for f in p.rglob('*'):
   if f.is_file():add(f)
 for name in NAMES:
  base=R/f'generated/revM/{name}';mf=read(f'generated/revM/{name}/manufacturing_manifest.json')
  for rel in ('manufacturing_manifest.json','viewer.json','meshes.bin','parts_bom.csv','procurement_routes.json','procurement_routes.csv','stock_quantity_summary.json','calibration_reference_plan.csv','joints.json','full_front.png','full_back.png',name.title()+'_RevM_assembly.step'):add(base/rel)
  for p in mf['parts']:
   add(base/p['STEP'])
   if 'print'in p:add(base/p['print']['STL'])
  for row in printmesh[name]['prints']:
   if row['print_process_STEP']:add(base/row['print_process_STEP'])
  for rel in mf['source_sha256']:add(R/rel)
  for rel in (f'harness/{name}_revM.json',f'harness/{name}_cut_list_revM.csv',f'mechanical_manifest/interfaces_revM_{name}.json',f'mechanical_manifest/wire_anchors_revM_{name}.json',f'mechanical_manifest/physical_{name}_41_capabilities.json',f'verification/revL_{name}.json'):add(R/rel)
 for d in ('generated/revM/assembly_details','generated/revM/electronics','generated/revM/firmware','verification/browser_revM','verification/firmware_revM'):tree(R/d)
 for p in (R/'tools').glob('*revM*'):
  if p.is_file():add(p)
 add(R/'tools/Build-RevM.ps1');add(R/'tools/run_cad.py');add(R/'tools/Start-Viewer.ps1');add(R/'Open-Viewer.cmd')
 for p in (R/'cad/revM').glob('*.py'):
  if not p.name.startswith(('probe_','inspect_')):add(p)
 for p in (R/'docs').glob('*REVM*.md'):add(p)
 for rel in ('START_HERE.zh-CN.md','README.md','docs/SOURCES.md','mechanical_manifest/network_revM.json','mechanical_manifest/support_policy.json','harness/topology.json','verification/REVM_REPORT.zh-CN.md','verification/revM_complete_audit.json','verification/revM_print_mesh_export.json','verification/revM_print_exports.json','verification/revM_print_process_clearance.json','verification/revM_proportions.json','verification/revM_kinematic_mapping.json','verification/revM_load_work.json','verification/revM_cover_assembly_access.json','verification/revM_strength_handling_screen.json','verification/revM_procurement_summary.json','verification/revM_electronics_package.json','verification/revM_firmware_package.json','verification/revM_firmware_build_work.json','verification/revM_offline_tests.json','verification/revM_export_summary.json','verification/revM_harness_power_manny.json','verification/revM_harness_power_quinn.json','verification/revM_python_tests.txt','generated/revM/RevM_Full_Body_Review.html'):add(R/rel)
 for d in (offline['source_sha256'],fw['source_sha256'],*[mapping['characters'][n]['source_sha256'] for n in NAMES]):
  for rel in d:add(REPO/rel)
 for p in (REPO/'Tools/PoseDollHardwareBridge').glob('*.cmd'):add(p)
 for p in (REPO/'Firmware/PoseDollFullBody/tests').glob('*'):
  if p.is_file():add(p)
 add(REPO/'Firmware/PoseDollFullBody/tools/run_core_tests.cmd')
 # Check current local Markdown links. Historical journals are deliberately excluded.
 bad=[]
 for p in sorted(files):
  if p.suffix!='.md' or not (p.parent==R/'docs' or p in (R/'START_HERE.zh-CN.md',R/'README.md',R/'verification/REVM_REPORT.zh-CN.md')):continue
  for link in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf-8')):
   link=link.strip('<>')
   if '://' in link or link.startswith('#'):continue
   target=link.split('#')[0]
   pending_manifest=(R/'generated/revM/delivery_manifest.json').resolve()
   if target and (p.parent/target).resolve()!=pending_manifest and not (p.parent/target).exists():bad.append([str(p.relative_to(REPO)),link])
 assert not bad,('broken current documentation links',bad)
 records=[dict(path=str(p.relative_to(REPO)).replace('\\','/'),bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(files)]
 write('generated/revM/delivery_manifest.json',dict(schema='posedoll.digital_delivery/1',created_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),status='DIGITAL_PROTOTYPE_CANDIDATE_NOT_MANUFACTURING_RELEASE',physical_tested=False,manufacturing_released=False,paths_relative_to='DollSimulation repository root',characters=characters,python_tests=offline['tests_run'],firmware_nodes=6,PCB_projects=4,browser_checked=True,files_count=len(records),files_total_bytes=sum(f['bytes'] for f in records),files=records,not_included=['CAD caches and intermediate revision outputs','manufactured samples or physical calibration','live UE bridge/Quinn adapter qualification']))
 print(json.dumps(dict(status='digital candidate complete',files=len(records),GiB=round(sum(f['bytes'] for f in records)/1024**3,3),characters={k:{i:v for i,v in d.items() if i not in ('source_cad_sha256','poses_with_nonadjacent_contacts')} for k,d in characters.items()}),ensure_ascii=False))
if __name__=='__main__':main()
