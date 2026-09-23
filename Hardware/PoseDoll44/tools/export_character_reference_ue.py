"""Run by UE Python commandlet; reads assets, writes reference files only."""
import unreal,json,datetime,traceback
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]  # Write into this design checkout, not the UE project
OUT=ROOT/'reference/ue58';OUT.mkdir(parents=True,exist_ok=True)
def vector(v):return [float(v.x),float(v.y),float(v.z)]
def bounds(b):return {'origin_cm':vector(b.origin),'extent_cm':vector(b.box_extent),'sphere_radius_cm':b.sphere_radius}
report={'engine':unreal.SystemLibrary.get_engine_version(),'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'assets':{},'read_only_assets':True}
for name in ('Manny','Quinn'):
 path='/Game/Characters/Mannequins/Meshes/SKM_'+name+'_Simple'
 mesh=unreal.load_asset(path)
 if not mesh:raise RuntimeError('Missing '+path)
 probe=json.loads(unreal.PoseDollEditorLibrary.inspect_rig(path,'/Game/Characters/Mannequins/Rigs/CR_Mannequin_Body'))
 if 'error' in probe:raise RuntimeError(probe['error'])
 probe['mesh_asset']=path;probe['skeleton_asset']=mesh.skeleton.get_path_name();probe['engine']=report['engine'];probe['utc']=report['utc']
 probe['imported_bounds']=bounds(mesh.get_imported_bounds());probe['extended_bounds']=bounds(mesh.get_bounds())
 (OUT/(name.lower()+'_mesh_probe.json')).write_text(json.dumps(probe,indent=2),encoding='utf8')
 dynamic=unreal.DynamicMesh()
 copied=unreal.GeometryScript_AssetUtils.copy_mesh_from_skeletal_mesh(mesh,dynamic,unreal.GeometryScriptCopyMeshFromAssetOptions(),unreal.GeometryScriptMeshReadLOD())
 if copied[-1]!=unreal.GeometryScriptOutcomePins.SUCCESS:raise RuntimeError('Cannot copy source geometry '+name)
 vectors=unreal.GeometryScript_MeshQueries.get_all_vertex_positions(dynamic,False)
 triangles=unreal.GeometryScript_MeshQueries.get_all_triangle_indices(dynamic,False)
 if vectors[-1] or triangles[-1]:raise RuntimeError('Sparse mesh requires explicit ID remapping')
 positions=unreal.GeometryScript_List.convert_vector_list_to_array(vectors[-2]);faces=unreal.GeometryScript_List.convert_triangle_list_to_array(triangles[-2])
 weights=[]
 for i in range(len(positions)):
  w=unreal.GeometryScript_BoneWeights.get_vertex_bone_weights(dynamic,i)
  if not w[-1]:raise RuntimeError('Missing skin weights at '+str(i))
  weights.append([[int(v.bone_index),float(v.weight)] for v in w[-2]])
 bone_info=unreal.GeometryScript_BoneWeights.get_all_bones_info(dynamic)
 info_array=bone_info[-1] if isinstance(bone_info,tuple) else bone_info
 (OUT/(name.lower()+'_bone_info_debug.json')).write_text(json.dumps([str(x) for x in info_array],indent=2),encoding='utf8')
 geo={'mesh_asset':path,'coordinate_system':'UE mesh local cm','positions_cm':[vector(v) for v in positions],'triangles':[[v.x,v.y,v.z] for v in faces],'skin_weights':weights,'bone_info':[{'name':str(v.name),'index':int(v.index),'parent_index':int(v.parent_index)} for v in info_array],'source':'GeometryScript CopyMeshFromSkeletalMesh source LOD0; no render deformation'}
 (OUT/(name.lower()+'_geometry.json')).write_text(json.dumps(geo,separators=(',',':')),encoding='utf8')
 report['assets'][name]={'mesh':path,'bones':len(probe['mesh_reference']),'vertices':len(positions),'triangles':len(faces),'imported_bounds':probe['imported_bounds']}

 print('PD44_EXPORT '+name+' '+json.dumps(report['assets'][name]))
(OUT/'extraction.json').write_text(json.dumps(report,indent=2),encoding='utf8')
unreal.log('PD44_REFERENCE_EXPORT_SUCCESS')
