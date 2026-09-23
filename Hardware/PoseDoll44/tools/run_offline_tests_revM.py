"""Record offline Python tests and C/Python golden framing compatibility."""
from pathlib import Path
import sys,json,hashlib,io,unittest,datetime
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT.parents[1];BRIDGE=REPO/'Tools/PoseDollHardwareBridge'
def main():
 sys.path.insert(0,str(BRIDGE));suite=unittest.defaultTestLoader.discover(str(BRIDGE),pattern='test_*.py');stream=io.StringIO();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
 (ROOT/'verification/revM_python_tests.txt').write_text(stream.getvalue(),encoding='utf-8')
 from pd41_protocol import encode_diagnostic,decode,FIXED
 golden=REPO/'Firmware/PoseDollFullBody/build_host/golden_pd41.bin';actual=golden.read_bytes();expected=encode_diagnostic(words=[FIXED]*3+[555]*41,timings=[[0,2000]]*6,device=0x123456789abc,boot=789,sequence=1,timestamp_us=1000,window_us=2000,presence=63);assert actual==expected,'C/Python golden frame mismatch';assert decode(actual[:-1])['pose_valid']
 files=[*BRIDGE.glob('*.py'),*ROOT.glob('mechanical_manifest/interfaces_revM_*.json'),ROOT/'mechanical_manifest/network_revM.json',REPO/'Tools/PoseDollSimulator/src/posedoll_sim/core.py',REPO/'Firmware/PoseDollFullBody/main/pd41_core.c',REPO/'Firmware/PoseDollFullBody/main/pd41_core.h',REPO/'Firmware/PoseDollFullBody/main/pd41_config.h',REPO/'Firmware/PoseDollFullBody/tests/core_test.c']
 out=dict(tested_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),tests_run=result.testsRun,failures=len(result.failures),errors=len(result.errors),skipped=len(result.skipped),passed=result.wasSuccessful(),C_Python_golden_match=True,golden_sha256=hashlib.sha256(actual).hexdigest(),core_scenarios=9,scope='offline synthetic tests; no hardware, serial, flashing or live UE',source_sha256={str(p.relative_to(REPO)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
 (ROOT/'verification/revM_offline_tests.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in out.items() if k!='source_sha256'}));return 0 if result.wasSuccessful() else 1
if __name__=='__main__':raise SystemExit(main())
