from pathlib import Path
import re,json,hashlib,datetime,subprocess
root=Path("Hardware/PoseDoll44").resolve();repo=root.parents[1]
broken=[];checked=0
for p in root.rglob("*.md"):
    text=p.read_text(encoding="utf-8-sig")
    for link in re.findall(r"\]\(([^)]+)\)",text):
        if "://" in link or link.startswith("#"):continue
        target=(p.parent/link.split("#")[0]).resolve()
        checked+=1
        if not target.exists():broken.append({"file":str(p.relative_to(root)),"target":link})
assert not broken,broken
firmware=repo/"Firmware/PoseDollHardware"
manifest={"recorded_at":datetime.datetime.now().astimezone().isoformat(),"idf":"6.1","target":"esp32s3","flash_size":"8MB","flashed":False,"sources":{},"binaries":{}}
for rel in ("main/main.c","main/CMakeLists.txt","CMakeLists.txt","sdkconfig.defaults"):
    manifest["sources"][rel]=hashlib.sha256((firmware/rel).read_bytes()).hexdigest()
for rel in ("build/posedoll_h1_diagnostic.bin","build/bootloader/bootloader.bin","build/partition_table/partition-table.bin"):
    p=firmware/rel
    assert p.exists(),rel
    manifest["binaries"][rel]={"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
(root/"verification/firmware_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf8")
result={"local_markdown_links_checked":checked,"broken_links":broken,"single_axis_render":"visually_reviewed","PCB_render":"visually_reviewed","physical_tests":"not_run","full_body_manufacturing_release":False}
(root/"verification/delivery_audit.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf8")
print(json.dumps(result))
