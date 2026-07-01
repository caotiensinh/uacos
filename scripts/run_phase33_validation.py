from pathlib import Path
import subprocess, sys, os, json, tempfile
ROOT=Path(__file__).resolve().parents[1]
env=os.environ.copy(); env['PYTHONPATH']=str(ROOT)+os.pathsep+env.get('PYTHONPATH','')
def main():
    with tempfile.TemporaryDirectory() as td:
        repo=Path(td)/'repo'; repo.mkdir(); (repo/'app.py').write_text('def value():\n    return 1\n',encoding='utf-8')
        cmds=[[sys.executable,'-m','uacos.cli','bootstrap','--repo',str(repo)],[sys.executable,'-m','uacos.cli','llm33-init','--repo',str(repo),'--ollama-lan','http://192.168.11.127:11434'],[sys.executable,'-m','uacos.cli','budget33-set','--repo',str(repo),'--max-cloud-tokens','10'],[sys.executable,'-m','uacos.cli','llm-run-real','--repo',str(repo),'--task','fix app value','--size','small'],[sys.executable,'-m','uacos.cli','budget33-status','--repo',str(repo)],[sys.executable,'-m','uacos.cli','llm33-status','--repo',str(repo)]]
        results=[]; ok=True
        for cmd in cmds:
            r=subprocess.run(cmd,cwd=ROOT,text=True,capture_output=True,env=env,timeout=120); results.append({'cmd':cmd,'returncode':r.returncode,'stdout':r.stdout[-4000:],'stderr':r.stderr[-1500:]}); ok=ok and r.returncode==0
        report={'status':'pass' if ok else 'fail','results':results}; out=ROOT/'phase33_validation_result.json'; out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8'); print(json.dumps(report,ensure_ascii=False,indent=2)); raise SystemExit(0 if ok else 1)
if __name__=='__main__': main()
