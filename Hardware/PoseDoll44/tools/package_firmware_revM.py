"""Copy tested node images with original offsets; does not communicate with hardware."""
from pathlib import Path
import hashlib,json,shutil
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 old=json.loads((ROOT/'verification/revM_firmware_build_work.json').read_text(encoding='utf-8'))
 for rel,digest in old['source_sha256'].items():assert sha(REPO/rel)==digest,rel
 rows=[]
 for row in old['nodes']:
  node=row['node'];src=REPO/f'Firmware/PoseDollFullBody/build_node{node}';dest=ROOT/f'generated/revM/firmware/node{node}';dest.mkdir(parents=True,exist_ok=True)
  assert sha(REPO/row['binary'])==row['sha256']
  cfg=(src/'sdkconfig').read_text();assert f'CONFIG_PD_NODE_ID={node}' in cfg
  args=json.loads((src/'flasher_args.json').read_text());files=[]
  for offset,rel in args['flash_files'].items():
   target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src/rel,target);files.append(dict(offset=offset,file=rel,bytes=target.stat().st_size,sha256=sha(target)))
  for name in ('flasher_args.json','sdkconfig'):shutil.copy2(src/name,dest/name)
  record=dict(node=node,chip=args['extra_esptool_args']['chip'],flash_settings=args['flash_settings'],images=files,hardware_flashed=False)
  (dest/'manifest.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8');rows.append(record)
 out=dict(nodes=rows,source_sha256=old['source_sha256'],built_with='ESP-IDF v6.1',hardware_flashed=False)
 (ROOT/'verification/revM_firmware_package.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
 print('Packaged',len(rows),'node image sets; offsets retained; no hardware accessed')
if __name__=='__main__':main()
