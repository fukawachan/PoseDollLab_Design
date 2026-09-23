"""Build all node configurations without opening hardware; record fresh evidence."""
from pathlib import Path
import subprocess,sys,json,hashlib,datetime
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 subprocess.run([sys.executable,str(REPO/'Firmware/PoseDollFullBody/tools/generate_config.py'),'--check'],cwd=REPO,check=True)
 fw=REPO/'Firmware/PoseDollFullBody';logs=ROOT/'verification/firmware_revM';logs.mkdir(exist_ok=True);rows=[]
 for node in range(1,7):
  run=subprocess.run(['powershell.exe','-NoProfile','-ExecutionPolicy','Bypass','-File',str(fw/'tools/build.ps1'),'-Node',str(node)],cwd=REPO,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  log=logs/f'node{node}_build.txt';log.write_bytes(run.stdout)
  if run.returncode:raise RuntimeError(f'Node {node} build failed; see {log}')
  build=fw/f'build_node{node}';cfg=(build/'sdkconfig').read_text();assert f'CONFIG_PD_NODE_ID={node}' in cfg
  binary=build/'posedoll_pd41.bin'
  if not binary.exists():
   args=json.loads((build/'flasher_args.json').read_text());binary=build/args['flash_files']['0x10000']
  rows.append(dict(node=node,binary=str(binary.relative_to(REPO)),bytes=binary.stat().st_size,sha256=sha(binary),build_log=str(log.relative_to(ROOT)),exit_code=0))
  print(f'Node {node}: build PASS, {binary.stat().st_size} bytes',flush=True)
 files=sorted((fw/'main').glob('*'))+[fw/'CMakeLists.txt',fw/'sdkconfig.defaults',fw/'tools/build.ps1',fw/'tools/generate_config.py']
 out=dict(tested_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),nodes=rows,all_six_final_builds_pending=False,source_sha256={str(p.relative_to(REPO)):sha(p) for p in files if p.is_file()},hardware_tested=False,flashed=False)
 (ROOT/'verification/revM_firmware_build_work.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
