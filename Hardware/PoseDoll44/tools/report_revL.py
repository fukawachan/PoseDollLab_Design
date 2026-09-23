"""Evidence-gated Rev L report. Never turn geometry into a fabrication release."""
from pathlib import Path
import json,hashlib,math
R=Path(__file__).resolve().parents[1]
def read(p):return json.loads((R/p).read_text('utf-8-sig'))
def save(p,v):(R/p).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
def sha(p):return hashlib.sha256((R/p).read_bytes()).hexdigest()

def main():
    tools=sum([read('verification/'+f)['checks'] for f in ('revL_legacy_tool_access.json','revL_twist_tool_access.json','revL_flex_tool_access.json')],[])
    assert len(tools)==176 and all(not c['unexpected_contacts'] for c in tools)
    sensor=read('verification/revL_readout_check.json');comps=read('verification/revL_components.json')
    assert len(sensor['isolated_flex_sweep'])==22 and all(not q['hits'] for q in sensor['isolated_flex_sweep'])
    assert len(comps['parts'])==24 and all(q['valid'] and q['solids']==1 for q in comps['parts'])
    assert sensor['source_sensor_step_sha256']==sha('generated/revK/components/sensor_revC_mini.step')
    old=read('verification/revK_design_audit.json')['source_and_output_snapshot_sha256']
    for p in ('electronics/sensor_revC_mini/PoseDoll_AS5048A_revC_mini.kicad_pcb','electronics/sensor_revC_mini/PoseDoll_AS5048A_revC_mini.kicad_sch','verification/sensor_revC_mini_erc.json','verification/sensor_revC_mini_drc.json'):
        assert sha(p)==old[p],p
    erc=read('verification/sensor_revC_mini_erc.json');drc=read('verification/sensor_revC_mini_drc.json')
    assert not erc.get('violations',[]) and not any(s.get('violations',[]) for s in erc.get('sheets',[]))
    assert not drc['violations'] and not drc['unconnected_items'] and not drc['schematic_parity']
    load=read('verification/revL_load_budget.json');viewer=read('verification/revL_viewer_geometry.json')
    variants={};table=[];loads=[];inventory=[];restriction=[];nearest=[]
    for name in ('manny','quinn'):
        rec=read(f'verification/revL_{name}.json');profile=f'mechanical_manifest/physical_{name}_44_revG_humanform_trial.json';p=read(profile)
        assert sha(profile)==old[profile]
        assert len(rec['parts'])==335 and len(rec['motion_checks'])==36 and rec['meta']['inherited_shapes_identity_verified']
        assert all(q['valid'] and q['solids']==1 for q in rec['parts']) and not rec['unexpected_new_assembly_contacts']
        limits={a['id']:a['limits_rad'] for a in p['axes']}
        for q in rec['motion_checks']+rec['focused_combination_checks']:
            for aid,angle in q['angles_deg'].items():
                low,high=limits[aid];assert low-1e-8<=math.radians(angle)<=high+1e-8
        assert all(q['structural_hits']==0 for q in rec['motion_checks'])
        assert len(rec['focused_combination_checks'])==6 and all(not q['hits'] for q in rec['focused_combination_checks'])
        assert len(sensor['channels'][name])==216
        for q in sensor['channels'][name]:
            gap=2.8 if q['axis_id'].endswith('.abduct') else 1.5
            assert abs(q['angle_error_deg'])<1e-6 and q['lateral_axis_error_mm']<1e-5 and abs(q['package_face_gap_mm']-gap)<1e-5
            assert q['nominal_geometric_zero_offset_deg']==(-90 if q['axis_id'].endswith('.flex') else 0)
        assert viewer[name]['parts']==335 and viewer[name]['poses']==36
        free=sum(not q['hits'] for q in rec['motion_checks']);axes=[]
        for aid in p['axis_order']:
            prefix,key=aid.split('.');active=prefix.startswith(('clavicle_','upperarm_','elbow_'))
            state='pelvis_reference_pending_no_fixed_stand' if prefix=='pelvis' else 'geometric_sensor_installation_unmeasured' if prefix.startswith('upperarm_') else 'girdle_envelope_only' if prefix.startswith('clavicle_') else 'elbow_transfer_envelope_only' if prefix.startswith('elbow_') else 'not_integrated'
            axes.append(dict(axis_id=aid,articulated=active,readout_status=state,holding_status='spring_clutch_candidate' if prefix.startswith('upperarm_') and key in ('flex','abduct') else 'incomplete',manufacturing_released=False))
        assert len(axes)==44 and sum(q['articulated'] for q in axes)==12 and sum(q['readout_status']=='geometric_sensor_installation_unmeasured' for q in axes)==6
        peak=load['variants'][name]['peak'];torque=peak['modeled_plus_100g_wrist_any_gravity_Nm'];margin=load['friction_torque_estimate_Nm_by_assumed_mu']['0.15']/torque
        assert margin>1.5
        closest=min(rec['new_sensor_to_chest_clearance'],key=lambda q:q['distance_mm'])
        variants[name]=dict(parts=335,articulated_axes=12,sensor_installation_candidates=6,axes=axes,samples=36,local_clear_samples=36,fully_clear_samples=free,focused_new_component_combinations=6,closest_new_sensor_to_chest=closest,holding_margin_assumed_mu_0p15=margin)
        table.append(f'| {name.title()} | 335 | 36/36 | {free}/36 | 6 |')
        nearest.append(f"| {name.title()} | {closest['pose']} | {closest['nearest_part']} | {closest['distance_mm']:.3f} |")
        loads.append(f"| {name.title()} | {peak['moving_model_mass_g']:.1f} | {torque:.3f} | {margin:.2f} |")
        restriction.extend(f"| {name.title()} | {q['pose']} | {len(q['hits'])} |" for q in rec['motion_checks'] if q['hits'])
        inventory.extend(dict(character=name,**q) for q in rec['parts'])
    save('mechanical_manifest/dual_character_mechanics_revL.json',dict(status='SIX_SHOULDER_READOUT_INSTALLATION_CANDIDATES',variants=variants,manufacturing_released=False,physical_tested=False,support_policy='mechanical_manifest/support_policy.json',fixed_external_stand_required=False,coverage_rule='Rigid segment shells, joint regions exposed',pending='Girdle readout, elbow transfer, girdle/twist holding and axial retention, full moving harness, torso/head/hands/legs, pelvis physical reference'))
    save('mechanical_manifest/revL_assembly_inventory.json',dict(status='CAD_INVENTORY_NOT_PURCHASE_BOM',rows=inventory,manufacturing_released=False))
    report='''# Rev L · 肩部屈伸测角检查

状态：数字设计候选，未制造放行、未实测。两款各新增左右屈伸安装；加上已有外展、扭转，每款六处肩关节测角安装候选。肩带不包括在这六处中。

## 总装检查

| 角色 | 实体及占位 | 无局部结构冲突 | 同时没有双臂互碰 | 肩关节测角安装 |
|---|---:|---:|---:|---:|
'''+ '\n'.join(table)+'''

原有 72 个离散肩臂姿态通过局部结构检查。阈值为相交体积 0.02 mm³。10 个独立双臂相交样本继续作为橙色摆姿限制；内部及相邻节段冲突仍标红。另有两款合计 12 个“肩带极限位置＋屈伸角度”组合，仅复查涉及本轮新增／修改件的配对，未发现相交；它们不能作为全总装新增姿态通过数。

检查先核对 Rev K 及其 Rev J 继承几何、比例和结果的 SHA256，并断言未改零件保持原 Shape 对象。原有未改件配对复用此前检查结果；每个姿态中涉及本轮变化的配对都重新做 BRep 相交。同一运动节段内的变化配对另行检查，只有明确螺钉／螺纹底孔对被解释为预期配合。

每款增加 46 个实体／占位，并修改 6 个既有实体，共 335 个；板上元器件也分别计数，**不是采购 335 件**。全部逻辑实体有效、单一实体。当前仍为 12/44 轴参与局部总装，人物比例、关节中心和原角度限位不变。

## 新组件与胸部承力框的距离

| 角色 | 最近的原有样本 | 最近零件 | 距离 / mm |
|---|---|---|---:|
'''+ '\n'.join(nearest)+'''

这些是名义 CAD 距离，不包含制造公差、手部挤压、骨架变形或完整躯干表面。小板背面基准从旧直排试放的 63.995 mm 改为 61.771 mm，缩短 2.224 mm。前期小板方向试排见 [研究记录](revL_head_probe.json)，它只检查了板与连接器包络，最终总装结论以本报告为准。

## 装配、测角与电路

- 64 条原离合／外展工具通道、36 条原扭转装配通道、76 条新增屈伸工具与插入检查通过，共 176 条。记录中明确区分工作台子装配与肩带上游尚未装入的阶段。
- 六处测角在两款各 36 姿态下完成 432 条同轴、相对角度及封装表面气隙检查。外展名义气隙为 2.8 mm；扭转和屈伸为 1.5 mm。
- 独立屈伸模块另检查 -50° 至 160° 每 10° 一个角度，共 22 项。新板的 90° 安装方向在 CAD 参考中产生 -90° 零位偏置，检查明确处理了该偏置；不是对真实传感器原始零值的预测。
- 沿用 Rev C mini 的原理图与 PCB。哈希核对确认它们及既有 ERC、DRC、未连接和原理图一致性结果未变，既有检查均为零项；本轮没有进行电子实测。

工具包络通过不等于装配扭矩、公差极限、手指抓握或无需拆解维修已经验证。FPC 只有短直插段，完整活动线束与转接没有完成。[详细装配顺序](../docs/SHOULDER_REVL.zh-CN.md)

## 持姿估算

| 角色 | 最不利轴下游已建质量 / g | 加每腕 100 g 的取样力矩上界 / N·m | μ=0.15、552 N 假设下的余量 |
|---|---:|---:|---:|
'''+ '\n'.join(loads)+'''

预算只覆盖现有屈伸和外展离合，按打印件实心 PLA、铝帽、钛螺钉与黄铜固定柱的假定密度计算；握力、动态、线束回弹、磨损与蠕变未计入验收。止挡高度保持原值，但铝帽的局部承压、螺纹强度和钛螺钉承载未验证，以上余量不是实测额定负载。完整假设见 [负载记录](revL_load_budget.json)。

## 双臂摆姿限制

| 角色 | 样本 | 独立双臂相交对数 |
|---|---|---:|
'''+ '\n'.join(restriction)+'''

## 交付与后续

[交互查看页](../generated/revL/RevL_Shoulder_Review.html) · [Manny STEP](../generated/revL/manny/Manny_shoulder_assembly.step) · [Quinn STEP](../generated/revL/quinn/Quinn_shoulder_assembly.step) · [独立屈伸测角组件 STEP](../generated/revL/components/flex_encoder_assembly.step)

[44 轴状态](../mechanical_manifest/dual_character_mechanics_revL.json) · [CAD 清单，非采购表](../mechanical_manifest/revL_assembly_inventory.json) · [源文件与结果快照](revL_design_audit.json)

肩带测角、肘部传角、肩带／扭转持姿、轴向保持、完整线束、躯干和下肢等继续待设计。人偶本体不依赖固定外部支架，外部支撑物暂不设计；站、坐、躺尚未进入完整全身检查。原骨盆三轴实体参考待定，通道名称保留兼容性。UE 插件、Python 模拟器与原下载方案未修改。现在不用打印、采购或补测工具。
'''
    (R/'verification/REVL_REPORT.zh-CN.md').write_text(report,encoding='utf8')
    paths=[]
    for pattern in ('cad/revL/*.py','cad/revL/*.html','verification/revL_*.json','generated/revL/components/*.step','generated/revL/*/*assembly.step','references/revL/*.json'):
        paths += [p for p in R.glob(pattern) if p.name!='revL_design_audit.json']
    paths += [R/p for p in ('START_HERE.zh-CN.md','tools/report_revL.py','tools/Build-RevL.ps1','tools/check_shoulder_browser.cjs','docs/SHOULDER_REVL.zh-CN.md','verification/REVL_REPORT.zh-CN.md','generated/revL/RevL_Shoulder_Review.html','mechanical_manifest/dual_character_mechanics_revL.json','mechanical_manifest/revL_assembly_inventory.json','mechanical_manifest/support_policy.json','generated/revK/components/sensor_revC_mini.step','verification/revK_design_audit.json','verification/revJ_design_audit.json')]
    paths += [R/key for key in old if key.startswith('cad/') or key.startswith('mechanical_manifest/physical_')]
    browser=read('verification/revL_browser_check.json') if (R/'verification/revL_browser_check.json').exists() else None
    browser_current=bool(browser and browser['htmlSha256']==sha('generated/revL/RevL_Shoulder_Review.html') and browser['checked_cases']==72 and not browser['errors'])
    save('verification/revL_design_audit.json',dict(source_and_output_snapshot_sha256={p.relative_to(R).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(set(paths))},baseline_geometry_sha_checked=True,all_original_axis_ids_preserved=True,all_angles_within_original_limits=True,local_clear_samples=72,focused_new_component_combinations=12,same_owner_new_contacts_clear=True,tool_and_insertion_checks=176,readout_checks=432,isolated_flex_samples=22,existing_PCB_checks_hash_verified=True,browser_verified=browser_current,manufacturing_released=False,physical_tested=False))
    print(json.dumps(dict(parts_per_model=335,shoulder_sensor_installations_per_model=6,local_clear_samples=72,focused_combinations=12,tool_and_insertion_checks=176,readout_checks=432,browser_verified=browser_current)),flush=True)
if __name__=='__main__':main()
