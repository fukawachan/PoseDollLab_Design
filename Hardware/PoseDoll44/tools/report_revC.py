"""Validate revision consistency, printable mesh topology and build a candid review report."""
from pathlib import Path
import json,hashlib,struct,collections,math,ast,re,datetime
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];V=ROOT/"verification"
def read(p):return json.loads(p.read_text(encoding="utf8"))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,d):p.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\n",encoding="utf8")
def mesh(path):
 data=path.read_bytes();n=struct.unpack_from("<I",data,80)[0];assert len(data)==84+50*n,path
 edges=collections.Counter();pts=[];volume=0
 for i in range(n):
  a=struct.unpack_from("<12fH",data,84+50*i);v=[tuple(round(x,5) for x in a[j:j+3]) for j in (3,6,9)]
  assert all(math.isfinite(x) for p in v for x in p),path
  for u,w in ((v[0],v[1]),(v[1],v[2]),(v[2],v[0])):edges[tuple(sorted((u,w)))]+=1
  pts.extend(v)
  a,b,c=v;volume+=(a[0]*(b[1]*c[2]-b[2]*c[1])-a[1]*(b[0]*c[2]-b[2]*c[0])+a[2]*(b[0]*c[1]-b[1]*c[0]))/6
 odd=sum(k!=2 for k in edges.values());dims=[max(p[j] for p in pts)-min(p[j] for p in pts) for j in range(3)]
 assert not odd,(path,odd)
 assert 0<volume and all(x<=160.01 for x in dims),(path,dims,volume)
 return {"path":path.relative_to(ROOT).as_posix(),"triangles":n,"non_manifold_edges":odd,"bbox_mm":dims,"signed_volume_mm3":volume}
def main():
 p=read(ROOT/"mechanical_manifest/physical_humanoid_44_revC_design.json");base=read(REPO/"Shared/Profiles/virtual_humanoid_44_v1.json")
 assert p["axes"]==base["axes"] and len(p["axes"])==44
 for a,b in zip(p["nodes"],base["nodes"]):
  for key in ("id","parent","axis_id","axis_local","kind"):assert a.get(key)==b.get(key),(a["id"],key)
  assert a["parent_to_axis"]["rotation_xyzw"]==b["parent_to_axis"]["rotation_xyzw"]
  assert a["axis_to_child"]==b["axis_to_child"]
 geom=read(V/"revC_initial_geometry.json");motion=read(V/"revC_motion_samples.json");h2=read(V/"H2_clutch_geometry.json");loads=read(V/"revC_load_sizing.json")
 step=ROOT/"generated/revC/step/sensor_revB.step";design=ROOT/"cad/revC/design.py"
 assert geom["source_sha256"]==sha(design) and not geom["neutral_collisions"]
 assert motion["complete"] and motion["sample_count"]==13
 assert motion["design_sha256"]==sha(design) and motion["sensor_step_sha256"]==sha(step)
 assert h2["source_sha256"]==sha(ROOT/"cad/revC/clutch.py") and h2["sensor_step_sha256"]==sha(step)
 assert loads["design_sha256"]==sha(design) and loads["source_sha256"]==sha(ROOT/"cad/revC/loads.py") and loads["sensor_step_sha256"]==sha(step)
 assert read(ROOT/"electronics/sensor_revB/mechanical_interface.json")["source_sha256"]==sha(ROOT/"electronics/sensor_revB/PoseDoll_AS5048A_revB.kicad_pcb")
 erc=read(V/"sensor_revB_erc.json");drc=read(V/"sensor_revB_drc.json")
 assert not drc["violations"] and not drc["unconnected_items"] and not drc["schematic_parity"]
 assert not any(s["violations"] for s in erc.get("sheets",[]))
 for fam,d in h2["families"].items():
  assert all(x["valid"] for x in d["parts"])
  assert all(x["solid_count"]==1 for x in d["parts"] if x["material"]=="printed")
  assert not d["fixed_rotating_intersections"] and not d["assembly_unplanned_intersections"],fam
  assert len(d["sweep_15deg"])==24 and not any(x["collisions"] for x in d["sweep_15deg"]),fam
 meshes=[mesh(f) for f in sorted((ROOT/"generated/revC/H2").rglob("*.stl"))]
 assert len(meshes)==12,len(meshes)
 for x in (ROOT/"cad/revC").glob("*.py"):ast.parse(x.read_text(encoding="utf8"))
 hits=[{"name":x["name"],"count":x["collision_count"],"collisions":x["collisions"]} for x in motion["poses"] if x["collisions"]]
 assert all(x["name"]=="hip_abduction" for x in hits),hits
 targets=sorted(loads["axis_loads"].items(),key=lambda item:-item[1]["sizing_hold_target_nm"])
 counter=collections.Counter(x["candidate_clutch_family"] for x in loads["axis_loads"].values())
 copy_mass=sum(h2["families"][f]["estimated_fixture_mass_g"]*n for f,n in counter.items())
 result={"recorded_at":datetime.datetime.now().astimezone().isoformat(),"digital_checks_completed":True,"manufacturing_release":False,"physical_tests":"not_run_deferred","user_testing_requested_now":False,"semantic_axes_preserved":44,"full_body_assembly_objects":geom["component_count"],"neutral_intersections":0,"motion_samples":13,"collision_free_samples":13-len(hits),"retained_self_contact_cases":hits,"H2_sweep_samples":72,"H2_unplanned_intersections":0,"H2_fixture_masses_g":{f:d["estimated_fixture_mass_g"] for f,d in h2["families"].items()},"H2_copy_mass_g_rejected_for_integration":copy_mass,"load_scenarios":loads["scenario_count"],"sampled_mass_budget_g":loads["mass_total_g"],"maximum_sample_hold_target":dict(axis=targets[0][0],**targets[0][1]),"printable_mesh_checks":meshes,"sensor_ERC_DRC_PARITY":"no_violations","remaining_design_work":["Integrate lighter friction cores with full-body fork structures, avoiding duplicated fixture frames.","Resolve true load/comfort requirements and full range/cable/hard-stop interference including final hardware.","Design fixed metal stand and grippable head/hands/feet interfaces.","Design the regional node/gateway/power boards and complete harness, firmware and end-to-end real 44-axis path.","Finalize machining drawings/tolerances, supplier parts and assembly/tool access before manufacturing release."],"evidence_limits":["Full-body model does not yet contain the H2 fixtures, final friction cores, cables, fixed stand or final fasteners.","H2 thread envelopes overlap their explicit mating minor holes; only listed thread engagement pairs are excluded.","Geometry samples do not prove continuous clearances, structural strength, friction life, EMC or sensor accuracy.","Named body samples are preset angle groups, not verification of hand-to-head/hip contact or grip ergonomics.","No simulator/UE code was modified or UE real-hardware acceptance claimed."]}
 save(V/"revC_review.json",result)
 lines=["# Rev C 数字设计审查", "", "**已完成这一版的数字检查；整机尚未达到制造放行状态。现在无需打印、采购或填写测量表。**", "", "## 当前证据", "",f"- 保留原来的 44 路轴 ID、排列、父子链和正方向；实体轴位单独导出。",f"- 全身模型 {geom['component_count']} 个装配对象，中立姿势无实体穿插。13 个离散姿势中 {13-len(hits)} 个无穿插。", "- 保留的碰撞：双腿外展 60° 且双臂垂下时，手腕与膝叉架相碰；把双臂外展 35° 后，同样的腿部姿势无穿插。没有从报告中删除原测试姿势。", "- H2 三种独立摩擦夹具：所有零件实体有效，所有非预期零件相交为零；每种按 15° 步长检查一圈，共 72 个角度样本，无动静干涉。", "- 12 个打印 STL 为闭合网格，逐件在 160 mm 包络内。它们仍是研究件，不是整机打印包。", "- 18×20 mm 双面 AS5048A 板：ERC、DRC、未连接项和原理图一致性均为零违规。", "", "## 负载与需要继续解决的问题", "",f"当前质量预算 {loads['mass_total_g']/1000:.2f} kg，含未建模五金/节点/线束余量；它不是实际 BOM 称重。{loads['scenario_count']} 个重力情景中，{targets[0][0]} 的样本保持目标最高，为 {targets[0][1]['sizing_hold_target_nm']:.2f} N·m。对应的全配置三角不等式上界目标为 {targets[0][1]['bound_hold_target_nm']:.2f} N·m。两者分别是抽样设计依据和保守上界，不能混称为已证实的最大负载。", "",f"H2 是便于逐层检查的独立夹具。按当前轴分级直接复制，光这些夹具就约 {copy_mass/1000:.2f} kg，不能装进 2.01 kg 的全身预算。正式关节必须与叉架共用支座，减少重复金属框架，再重新计算质量、运动和持姿力。", "", "完整摩擦组件、最终紧固件、线束/插头弯曲空间、固定支架、区域节点与网关都还没有进入全身可制造装配。**这些是尚未完成的设计工作，不能归因于用户没有实测。**", "", "## 可查看的文件", "", "- [最新入口](../START_HERE.zh-CN.md)", "- [全身 STEP](../generated/revC/step/HW44_revC_candidate.step)", "- [H2 结构与装配说明](../docs/H2_CLUTCH.zh-CN.md)", "- [完整机器可读审查](revC_review.json)", "- [全部碰撞样本](revC_motion_samples.json)", "- [负载计算及每项质量假设](revC_load_sizing.json)", "", "全部物理验收继续保持 not_run/null。数字检查没有覆盖实物摩擦、磁场串扰、磨损、供电、总线和 UE 全身实时链路。"]
 (V/"REVC_REPORT.zh-CN.md").write_text("\n".join(lines)+"\n",encoding="utf8")
 files=[f for folder in (ROOT/"cad/revC",ROOT/"generated/revC",ROOT/"electronics/sensor_revB") for f in folder.rglob("*") if f.is_file() and "__pycache__" not in f.parts and f.suffix not in (".pyc",)]
 save(V/"revC_artifact_sha256.json",{f.relative_to(ROOT).as_posix():sha(f) for f in sorted(files)})
 print(json.dumps({"axes":44,"meshes":len(meshes),"body_clear_samples":13-len(hits),"H2_angles":72,"physical_tests":"not_run","manufacturing_release":False}))
if __name__=="__main__":main()
