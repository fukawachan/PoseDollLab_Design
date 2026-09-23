"""Generate the review report and vector drawings from actual verification artifacts."""
from pathlib import Path
import json,html,hashlib,datetime,shutil
ROOT=Path(__file__).resolve().parents[1]
def read(p):return json.loads((ROOT/p).read_text(encoding="utf-8-sig"))
def write(p,s):
    path=ROOT/p;path.parent.mkdir(parents=True,exist_ok=True);path.write_text(s,encoding="utf8")
def svg_start(w,h,title):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="#f5f7fa"/><g font-family="Microsoft YaHei UI, Microsoft YaHei, sans-serif" fill="#17283b">',f'<text x="35" y="45" font-size="25">{html.escape(title)}</text>']
def txt(s,x,y,text,size=15):s.append(f'<text x="{x}" y="{y}" font-size="{size}">{html.escape(str(text))}</text>')
def drawings():
    fits=read("mechanical_manifest/print_fit_profile_revB.json")
    s=svg_start(1000,1200,"H1 未来试片 Rev B · 单位 mm · 示意图非 1:1")
    txt(s,35,82,"目前继续数字设计，无需打印或测量；本图留待设计完成后的实物验证。",19)
    txt(s,35,117,"H1-001：左下大切角 + 右上小切角；从下到上 M2 / M3 / M4 / M6 / POM。",17)
    x0,y0,k=160,170,5
    w,h,t=fits["coupon"]["size_mm"]
    s.append(f'<path d="M{x0} {y0} H{x0+w*k-15} L{x0+w*k} {y0+15} V{y0+h*k} H{x0+30} L{x0} {y0+h*k-30} Z" fill="#d9e6ed" stroke="#304c62" stroke-width="2"/>')
    for row in fits["coupon"]["rows_bottom_to_top"]:
        y=y0+(h/2-row["y_mm"])*k
        txt(s,55,y+5,row["id"],19)
        for c,d in enumerate(row["diameters_mm"]):
            x=x0+(11+c*22)*k
            selected=(d==fits["clearance_holes_mm"].get(row["id"]) or (row["id"]=="POM10" and d==fits["bushing"]["housing_d_mm"]))
            s.append(f'<circle cx="{x}" cy="{y}" r="{d*k/2}" fill="{("#cce7cf" if selected else "white")}" stroke="#304c62"/>')
            txt(s,x-17,y-d*k/2-9,f"{d:g}",15)
    for c in range(5):txt(s,x0+(11+c*22)*k-6,153,chr(65+c),20)
    txt(s,160,573,"110 × 74 × 6；绿色为当前 CAD 候选值，不表示已经验证。",18)
    txt(s,160,600,"M3 的 D 孔 3.8 用于多片支架长螺栓；M5 尚无 H1 实际用途。",16)
    txt(s,35,641,"H1-002：M3 螺母对边 AF / Ø6 磁铁槽；同样有两个不同大小切角。",17)
    s.append('<path d="M210 680 H625 L640 695 V880 H240 L210 850 Z" fill="#e7dfd0" stroke="#66573f" stroke-width="2"/>')
    import math
    for i,af in enumerate(fits["nut_M3"]["coupon_af_mm"]):
        x=210+(13+i*20)*5;y=680+12*5;rr=af/math.cos(math.pi/6)*2.5
        pts=" ".join(f"{x+rr*math.cos(math.pi*a/3):.2f},{y+rr*math.sin(math.pi*a/3):.2f}" for a in range(6))
        s.append(f'<polygon points="{pts}" fill="white" stroke="#66573f"/>')
        txt(s,x-27,y-29,f"{chr(65+i)} {af:g}")
        d=fits["magnet"]["coupon_d_mm"][i];y=680+30*5
        s.append(f'<circle cx="{x}" cy="{y}" r="{d*2.5}" fill="white" stroke="#66573f"/>')
        txt(s,x-20,y-27,f"Ø{d:g}")
    txt(s,210,910,f'86 × 40 × 8；螺母槽深 {fits["nut_M3"]["pocket_depth_mm"]:g}，磁铁槽深 {fits["magnet"]["seat_depth_mm"]:g}。',17)
    txt(s,35,957,"H1-003：底座朝下，从左到右 A–E；厚度设计保持不变。",18)
    for i,v in enumerate((1,1.5,2,2.5,3)):
        x=185+i*110
        s.append(f'<rect x="{x}" y="987" width="65" height="85" fill="#d7e7e3" stroke="#355e54"/>')
        txt(s,x+4,1020,chr(65+i),18);txt(s,x+4,1050,f"{v:g} mm")
    txt(s,35,1120,"测试时使用实际装配件，不另买四根圆棒。当前所有实测记录仍为空。",18)
    txt(s,35,1160,"旧 Rev A H1-001 只有四排孔，不能按这张 Rev B 图填写；无需现在补打。",17)
    s.append("</g></svg>");write("generated/drawings/coupon_map.svg","\n".join(s))
    s=svg_start(950,770,"H1 主轴堆叠 · Z=0 为底座顶面")
    layers=[("-6～0","H1-010 底座"),("0～3","下钢环 3"),("3～4.5","下钢环 1.5"),("4.5～6","下摩擦环"),("6～25","H1-013 转子 / 两端轴套"),("25～26.5","上摩擦环"),("26.5～28","上钢环"),("28～31","压环"),("31～36","H1-012 上叉"),("59.4～61.9","Ø6×2.5 磁铁"),("62～62.8","H1-015 圆盖"),("63.2～64.4","AS5048A 封装"),("64.4～66","自制 PCB"),("66～70","H1-017 托架"),("71～76","H1-016 支撑臂")]
    txt(s,35,80,"展开顺序示意，非比例剖面；力从压环/摩擦环传递，PCB 不承重。")
    for i,(z,n) in enumerate(reversed(layers)):
        y=107+i*38
        s.append(f'<rect x="245" y="{y}" width="190" height="27" fill="{("#c9dbe8" if i%2 else "#e2d5b9")}" stroke="#485e70"/>')
        txt(s,40,y+19,z,17);txt(s,460,y+20,n,17)
    txt(s,35,715,"固定黄铜套 OD8 / ID6.4 / L31 独立于摩擦叠层；预紧/载荷待审查。")
    txt(s,35,746,"磁铁到芯片名义 1.3 mm，盖到芯片 0.4 mm；不是已完成的公差分析。")
    s.append("</g></svg>");write("generated/drawings/axial_stack.svg","\n".join(s))
    s=svg_start(940,650,"H1 自制传感器板 Rev A · 接线审查")
    txt(s,35,80,"从 PCB 元件面看，J1 在上方。此图不是线束插头端面图。")
    s.append('<rect x="60" y="130" width="310" height="310" fill="#d9e9de" stroke="#315d43" stroke-width="3"/>')
    for x in (89,341):
        for y in (159,411):s.append(f'<circle cx="{x}" cy="{y}" r="10.7" fill="white" stroke="#315d43"/>')
    s.append('<rect x="176" y="260" width="60" height="42" fill="#344944"/>')
    txt(s,180,328,"U1")
    pads=sorted((v for v in read("electronics/sensor_revA/pad_map.json") if v["ref"]=="J1" and v["pad"].isdigit()),key=lambda v:v["x_mm"])
    for i,p in enumerate(pads):
        x=170+i*19
        s.append(f'<rect x="{x}" y="145" width="12" height="30" fill="#be9950"/>')
        txt(s,x+1,138,p["pad"],15)
    txt(s,90,475,"PCB 32×32 / 孔距26 / 孔Ø2.2")
    nets=[("1","GND","GND / J1-22"),("2","+3V3","3V3 / J1-1 或2"),("3","SCK","GPIO12 / J1-18"),("4","MOSI","GPIO11 / J1-17"),("5","MISO","GPIO13 / J1-19"),("6","CS_N","GPIO10 / J1-16")]
    txt(s,435,155,"自制板 J1       信号       ESP32-S3 DevKitC-1",18)
    for i,(p,n,g) in enumerate(nets):
        y=205+i*43;txt(s,455,y,p,20);txt(s,515,y,n,18);txt(s,635,y,g,18)
    txt(s,35,535,"仅 3.3V；先断电连接；线束由供应商预焊并逐线检查。",20)
    txt(s,35,575,"官方 AS5048A 评估板 P1 不同，不能照抄本图编号。")
    txt(s,35,615,"SPI mode 1 / 250 kHz · 原生 USB19/20 保留 · 当前 H1 不接 CAN")
    s.append("</g></svg>");write("generated/drawings/wiring.svg","\n".join(s))
def reports():
    b=read("verification/budgets.json");g=read("verification/generation_summary.json")
    exact=read("verification/exact_geometry_screen.json");d=read("verification/design_consistency.json")
    lines=["# H0 工程报告 · 整机布局 Rev A / 机械配合 Rev B", "", "结论：继续数字设计，不以用户先完成试片实测为前提。Rev B 按 A1 mini / 0.4 mm / PLA 的工程假设调整通孔并生成未来试片；当前不要求用户打印或测量。整机制造与实物性能尚未验证。", "",
    "## 已执行", "",f"- {g['axis_count']} 轴映射，六区域 6/6/9/9/7/7；原虚拟轴顺序一致。",f"- {g['part_count']} 个编号打印件均为单一有效实体，单件包络不超过 160 mm；3 件 fit 试片留作设计完成后的验证。",
    "- 单轴 0～145° 每 5° 共 30 个名义姿态：本模型参与检查的动/静实体无正体积干涉。不是连续扫角、公差或承载证明。",
    "- KiCad ERC、DRC 与原理图一致性检查通过；详细启用/忽略规则见 JSON 报告，未添加违规豁免来隐藏失败。",
    "- 单轴诊断固件在 ESP-IDF 6.1 编译；协议故障测试、诊断界面构造和现有模拟器测试已运行，见对应日志。",
    "- 现有受版本管理的软件文件没有修改。本轮没有运行实体 UE Capture/Undo/重开测试。", "",
    "## 布局与负载", "", f"中立头顶参考点 Z={g['neutral_head_tip_mm'][2]:.0f} mm，已超过原约500 mm目标；不是尺寸冻结。质量集中参数预算为 {b['estimated_total_kg']:.3f} kg，不是称重。区域/网关 PCB、连接器维护空间和支架是候选包络。",
    "", "三类关节是尺寸/能力假设：", "", "|类别|圆柱半径×轴向长 mm|主螺栓/轴 mm|能力假设 Nm|模块质量假设 g|","|---|---|---|---|---|"]
    for n,v in read("mechanical_manifest/families.json").items():lines.append(f"|{n}|{v['radius_mm']}×{v['axial_mm']}|{v['shaft_mm']}|{v['design_capacity_nm']}|{v['module_mass_g']}|")
    lines += ["","H1 是较宽敞的台架夹具，不能当作已封装的 S/M/L 身体模块。当前 32 mm 传感器板和紧凑多轴支架还需共同缩小/避让。","",
    "预算采用 τ=轴方向·Σ(r×mg)；对给定形状另列 Σ(mg·垂轴距离) 的方向无关上界。后者是保守包络，**不是已经出现的实际最坏负载**；保持目标按上界×1.5+0.02 Nm 线束余量。质量集中、线束余量与能力假设都需实物修正。","",
    "|轴|12姿态重力最大 Nm|方向无关上界 Nm|设计保持目标 Nm|能力假设 Nm|","|---|---:|---:|---:|---:|"]
    for a in sorted(b["axes"],key=lambda a:a["holding_design_target_nm"],reverse=True)[:8]:
        lines.append(f"|{a['axis_id']}|{a['sampled_gravity_max_nm']}|{a['orientation_independent_bound_nm']}|{a['holding_design_target_nm']}|{a['family_capacity_hypothesis_nm']}|")
    lines += ["","结论：当前大关节能力假设无法覆盖保守预算。需要减重、收拢轴中心、重新布置支架和夹持面，而不能直接拧紧所有关节。强度/蠕变/疲劳未做结论。","",
    "## 碰撞与走线","","完整布局保留 12 个具名姿态和 64 个固定种子随机姿态的球包络筛查。进一步对 12 个姿态中的关节、传感器板、区域板与接头维护包络做了 OCC 交集：","","|姿态|相交包络对数|","|---|---:|"]
    for n,v in exact["full44"]["poses"].items():lines.append(f"|{n}|{v['interference_count']}|")
    lengths=read("harness/sensor_lengths.json")
    lines += ["","这些是实心设计包络的相交，不全等于真实空心支架撞击；它们也**不能被忽略当作已解决**。需要紧凑三轴支架详细设计和连续运动/工具/线束审查。具名姿态是设定角度，不证明手实际碰到额头或髋部。","",
    f"六区域节点位置已调整。12 姿态中的端点直线距离+60 mm 假设余量上取整后，44 条最长 {max(v['minimum_envelope_length_plus_60mm'] for v in lengths)} mm。它不是沿关节表面的走线长度，更不是可裁线单；弯曲、应力释放、插拔空间仍待设计。",
    "CAN 候选线性顺序 G0→N1→N5→N6→N3→N2→N4，端点终端，电源单独分路。不是把多个分支星形连成 CAN。","",
    "## 电气预算与实现范围","",
    f"44传感器、6 MCU、7 CAN收发器及缓冲余量，按3.3V负载和85%降压效率估算，5V输入 {b['power']['estimated_5v_A']} A；加30%余量 {b['power']['with_30_percent_margin_A']} A。5V/4A仅为候选规格，未选择适配器或完成保护/热设计。",
    f"九传感器区域若用线性稳压，预算耗散 {b['power']['regional_linear_ldo_dissipation_W_at_9_sensors']} W，因此完整区域应设计降压电源，不能照抄台架DevKit的供电。",
    "CAN：17帧/周期×100Hz×135bit + 60诊断帧/秒×135bit，500kbit/s下约47.52%；未含实测重发和错误风暴，不是通过60%占用目标的证据。",
    f"支架粗估力矩 {b['stand']['moment_estimate_Nm_at_150mm_plus_20N_at_400mm']:.2f} Nm（重心150mm + 手20N作用于400mm），桌夹/桌面未选型。","",
    "只完成自制传感器板与单轴USB诊断。区域节点/网关PCB、保护/隔离供电、CAN固件、完整cohort USB协议、UE实体设备配置和校准尚未实现。无采购生产Gerber，无烧录、OTP写入或实物通电。","",
    "## Rev B 打印配合设计依据","",
    "已读取用户提供的《PLA材料比较》对话，并核对官方补偿功能文档及一条社区原始反馈。社区个例不作为精度保证。当前孔径：M2 2.6、M3 3.6、M4 4.8、M6 6.8 mm；多片支架 M3 3.8 mm。M5 5.8 mm 仅保留规则。",
    "CAD 中的装配余量与切片补偿分开记录；未来切片初始 XY 补偿为0、自动圆孔补偿关闭，避免叠加未标定修正。轴套座和磁铁座单独处理，不套用螺丝通孔余量。",
    "孔径误差 -0.4/-0.2/0/+0.1 mm 只是敏感性情景，不是实测分布；参见 print_fit_sensitivity.json 与 [设计依据](../docs/DESIGN_BASIS.zh-CN.md)。这些假设不能证明定位、承载或所有打印方向合格。","",
    "## 继续设计与后续实物验证","",
     "1. 采用 print_fit_profile_revB.json 中的未标定假设继续设计；不等待用户补工具或试片。","2. 设计端继续完成轴套保持、磁铁定心、五金选型、紧固件和工具净空；在最终实物测试包中明确装配件与检验方法。","3. 完成紧凑三轴详细结构，实测相邻磁铁、负载与手感后扩展一侧肢体。","4. 节点/网关与UE实体链路独立验收后进入全44台架和整机。","",
    f"软件基线：{d['baseline_commit']}。原profile SHA256：{d['baseline_profile_sha256']}。"]
    write("verification/H0_REPORT.md","\n".join(lines)+"\n")
    checklist="""# H1 放行检查表

| 项目 | 状态 | 证据/条件 |
|---|---|---|
| 44轴ID、顺序及分区 | 数字通过 | design_consistency.json |
| 13个打印实体与打印包络 | 数字通过 | cad_parts.json |
| 打印配合假设 | Rev B，未实测标定 | print_fit_sensitivity.json、../docs/DESIGN_BASIS.zh-CN.md |
| 导出 STEP 代表性孔径 | 数字检查 | fit_geometry_check.json；不代表实际孔径 |
| 单轴名义30姿态实体检查 | 数字通过（有限范围） | exact_geometry_screen.json |
| 传感器ERC/DRC/网表一致性 | 数字通过（记录规则集） | sensor_erc.json、sensor_parity_drc.json |
| 诊断协议与故障恢复 | 软件测试 | h1_protocol_tests.txt |
| 中文诊断窗口 | 构造通过，无串口连接 | diagnostic_gui_smoke.txt |
| 固件 | 编译通过，无烧录 | firmware_build.txt |
| 原模拟器 | 回归通过 | simulator_regression.txt |
| 三件尺寸试片文件 | Rev B，留作以后验证 | generated/stl_fit，仅H1-001/002/003；现在不要求打印 |
| 试片实际尺寸/配合 | deferred / not_run | 用户暂无工具；设计继续，实测安排在设计完成后 |
| 实际模块/磁铁/五金尺寸冻结 | 未完成 | 供应商修订与工单 |
| 承载关节制造放行 | 未放行 | 公差、材料、预紧、紧固件和工具空间待审查 |
| 自制PCB制造放行 | 未放行 | 元器件实物/装配/供电/信号完整性审查 |
| 单轴上电、绝对误差、重复性、静止噪声 | not_run | 独立基准与原始日志 |
| 持姿、摩擦力、1000次磨耗、磁串扰 | not_run | 负载和方法先审查 |
| 全身结构/线束冻结 | 未放行 | 完整三轴几何与碰撞限制仍在 |
| CAN/全44台架/60分钟运行 | not_run | 节点及网关尚未实现 |
| 实体UE预览/Capture/Undo/重开 | not_run | 实体配置与校准尚未实现 |

不得通过把缺失轴填零、修改旧golden vectors、忽略传感器故障或隐藏碰撞来改变这些结论。目标值见 physical_acceptance.json，实际值保持空值。

本轮未采购、下单、烧录或远程打印。用户已明确先继续设计，后做实物测试。试片文件存在不等于现在需要打印，工程假设不等于经过机器标定。
"""
    write("verification/H1_RELEASE_CHECKLIST.md",checklist)
    metrics=[("axis_absolute_error","<=1.5 deg, independent reference <=0.3 deg uncertainty"),("axis_repeatability","<=0.5 deg"),("static_noise","<=0.15 deg RMS / 10s"),("magnetic_crosstalk","<=0.3 deg"),("pose_holding","<=1 deg / 5min at declared load"),("early_wear_screen","1000 cycles"),("internal_acquisition","100Hz complete fresh cohort"),("ue_stream","60Hz"),("acquisition_window","<=5ms"),("can_bus_load","<60% measured"),("fault_reporting","<=100ms after detection"),("system_soak",">=60min")]
    if not (ROOT/"verification/physical_acceptance.json").exists():
        write("verification/physical_acceptance.json",json.dumps({"metrics":[{"id":n,"target":t,"status":"not_run","evidence":None,"measured_value":None} for n,t in metrics]},indent=2))
    # Snapshot source and generated STL hashes for the reviewed iteration.
    data={}
    for directory in ("cad","tools","mechanical_manifest","docs","generated/stl_fit","generated/stl_draft","electronics/sensor_revA"):
        for path in sorted((ROOT/directory).glob("*")):
            if path.is_file() and path.suffix not in (".pyc",".kicad_prl"):
                data[path.relative_to(ROOT).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    write("verification/artifact_sha256.json",json.dumps(data,indent=2))
def main():
    drawings();reports()
    print("H0/H1 reports, vector drawings and artifact hashes generated")
if __name__=="__main__":main()
