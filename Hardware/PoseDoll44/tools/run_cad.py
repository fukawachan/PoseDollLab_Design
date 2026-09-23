"""Run CadQuery from the already installed CQ-editor 2.7 bundle (Python 3.13).
No installation or changes to the simulator environment. Standard cadquery
installations also work: python cad/build.py. This adapter is local tooling.
"""
from pathlib import Path
import sys, os, struct, marshal, zlib, importlib.abc, importlib.util, runpy, json, hashlib
EXE=Path(r"D:/ProgramFiles/CQ-editor/CQ-editor.exe")
ROOT=Path(__file__).resolve().parents[1]
def bootstrap():
    candidates=sorted(Path(os.environ["TEMP"]).glob("_MEI*"),key=lambda p:p.stat().st_mtime,reverse=True)
    bundle=next((p for p in candidates if (p/"cadquery-2.7.0.dist-info").exists()),None)
    if bundle is None: raise RuntimeError("Start the installed CQ-editor, or use a normal CadQuery 2.7 Python environment.")
    data=EXE.read_bytes(); magic=b"MEI\x0c\x0b\x0a\x0b\x0e"; cookie=data.rfind(magic)
    _,length,tocpos,toclen,ver,pylib=struct.unpack("!8sIIII64s",data[cookie:cookie+88])
    if ver!=sys.version_info.major*100+sys.version_info.minor: raise RuntimeError("Use Python 3.13 matching CQ-editor")
    start=cookie+88-length; pos=start+tocpos; end=pos+toclen
    while pos<end:
        n,off,clen,ulen,compressed,kind=struct.unpack("!iIIIBc",data[pos:pos+18])
        name=data[pos+18:pos+n].rstrip(b"\0").decode()
        if kind==b"z":
            pyz=data[start+off:start+off+clen]; pyz=zlib.decompress(pyz) if compressed else pyz
            break
        pos+=n
    else: raise RuntimeError("PYZ archive not found")
    if pyz[:4]!=b"PYZ\0" or pyz[4:8]!=importlib.util.MAGIC_NUMBER: raise RuntimeError("Python bytecode mismatch")
    toc=dict(marshal.loads(pyz[struct.unpack("!i",pyz[8:12])[0]:]))
    class BundleLoader(importlib.abc.MetaPathFinder,importlib.abc.Loader):
        def find_spec(self,fullname,path=None,target=None):
            if fullname not in toc: return None
            kind,off,n=toc[fullname]
            if kind not in (0,1,3): return None
            return importlib.util.spec_from_loader(fullname,self,is_package=bool(kind))
        def create_module(self,spec): return None
        def exec_module(self,module):
            kind,off,n=toc[module.__name__]
            p=bundle.joinpath(*module.__name__.split("."))
            module.__file__=str(p/"__init__.pyc" if kind else p.with_suffix(".pyc"))
            if kind: module.__path__=[str(p)]
            if kind != 3: exec(marshal.loads(zlib.decompress(pyz[off:off+n])),module.__dict__)
        def get_data(self,p): return Path(p).read_bytes()
    sys.path.insert(0,str(bundle))
    sys.meta_path.insert(0,BundleLoader())
    handles=[os.add_dll_directory(str(p)) for p in [bundle,*bundle.glob("*.libs"),bundle/"OCP",bundle/"vtkmodules",bundle/"casadi"] if p.is_dir()]
    globals()["_dll_handles"]=handles
    import cadquery as cq
    return {"cadquery":cq.__version__,"python":sys.version,"cq_editor_sha256":hashlib.sha256(data).hexdigest(),"bundle":str(bundle)}
if __name__=="__main__":
    info=bootstrap()
    if len(sys.argv)<2:
        import cadquery as cq
        s=cq.Workplane("XY").box(10,10,10).val()
        print(json.dumps({**info,"solid_valid":s.isValid(),"volume_mm3":s.Volume()},indent=2))
    else:
        target=Path(sys.argv[1]).resolve(); sys.argv=sys.argv[1:]
        sys.path.insert(0,str(target.parent))
        runpy.run_path(str(target),run_name="__main__")
