from __future__ import annotations
from pathlib import Path
from datetime import datetime, timezone
import json
from uacos.config import uacos_dir
from uacos.compression.engine import compressed_context
from uacos.budget.optimizer import classify_task
from uacos.llm.real_providers import run_with_fallback, init_real_llm, load_real_config, provider_probe
from uacos.token.budget_guard import load_budget
from uacos.cache.llm_cache import make_cache_key, get_cache, put_cache, find_similar, cache_status as llm_cache_status

def utcnow(): return datetime.now(timezone.utc).isoformat()
def llm33_dir(repo_root: Path): p=uacos_dir(repo_root)/'llm33'; p.mkdir(parents=True,exist_ok=True); return p
def history_path(repo_root: Path): return llm33_dir(repo_root)/'llm33_history.jsonl'
def append_history(repo_root,row): row=dict(row); row.setdefault('ts',utcnow()); history_path(repo_root).open('a',encoding='utf-8').write(json.dumps(row,ensure_ascii=False)+'\n')
def build_llm_prompt(repo_root,task,size=None,max_tokens=6000):
    size=size or classify_task(task).get('size','small'); ctx=compressed_context(repo_root,task,max_tokens=max_tokens,max_files=8); prompt=f"""UACOS REAL LLM TASK\n\nTask:\n{task}\n\nRules:\n- Return concise analysis.\n- If code changes are needed, return a valid unified diff.\n- Do not invent files not present in context unless explicitly necessary.\n- Keep patch minimal and safe.\n\nContext:\n{ctx['content']}\n"""; out=llm33_dir(repo_root)/'latest_llm33_prompt.md'; out.write_text(prompt,encoding='utf-8'); return {'status':'ok','size':size,'prompt':prompt,'prompt_file':str(out),'context':{k:v for k,v in ctx.items() if k!='content'}}
def llm_run_real(repo_root,task,size=None,real=False,max_context_tokens=6000,use_cache=True,similar_threshold=0.82):
    init_real_llm(repo_root)
    prompt_data=build_llm_prompt(repo_root,task,size=size,max_tokens=max_context_tokens)
    cache_key=make_cache_key(task,prompt_data['prompt'],size=prompt_data['size'])
    if use_cache:
        cached=get_cache(repo_root,cache_key)
        if not cached:
            cached=find_similar(repo_root,task,threshold=similar_threshold)
        if cached:
            result=cached.get('result',{})
            record={'task':task,'size':prompt_data['size'],'real':real,'cache_hit':True,'hit_type':cached.get('hit_type'),'cache_key':cached.get('key'),'result':{k:v for k,v in result.items() if k!='content'}}
            append_history(repo_root,record)
            return {'status':'cache_hit','hit_type':cached.get('hit_type'),'similarity':cached.get('similarity'),'size':prompt_data['size'],'provider':result.get('provider'),'model':result.get('model'),'usage':{'total_tokens':0,'saved_estimated_tokens':(result.get('usage') or {}).get('total_tokens') or result.get('estimated_tokens',0)},'attempts':result.get('attempts'),'reason':None,'prompt_file':prompt_data['prompt_file'],'response_file':result.get('response_file'),'budget':load_budget(repo_root),'cache_key':cached.get('key')}
    result=run_with_fallback(repo_root,prompt_data['prompt'],size=prompt_data['size'],real=real)
    record={'task':task,'size':prompt_data['size'],'real':real,'prompt_file':prompt_data['prompt_file'],'cache_hit':False,'result':{k:v for k,v in result.items() if k!='content'}}
    if result.get('content'):
        out=llm33_dir(repo_root)/'latest_llm33_response.md'; out.write_text(result['content'],encoding='utf-8'); record['response_file']=str(out); result['response_file']=str(out)
    if use_cache and result.get('status') in {'ok','dry_run'}:
        put_cache(repo_root,cache_key,task,prompt_data['prompt'],{k:v for k,v in result.items() if k!='raw'},meta={'size':prompt_data['size'],'real':real})
    append_history(repo_root,record)
    return {'status':result.get('status'),'size':prompt_data['size'],'provider':result.get('provider'),'model':result.get('model'),'usage':result.get('usage') or ({'total_tokens':result.get('estimated_tokens')} if result.get('estimated_tokens') else None),'attempts':result.get('attempts'),'reason':result.get('reason'),'prompt_file':prompt_data['prompt_file'],'response_file':result.get('response_file'),'budget':load_budget(repo_root),'cache_key':cache_key,'cache_used':False}

def llm33_status(repo_root):
    init_real_llm(repo_root); cfg=load_real_config(repo_root); probes={name:provider_probe(repo_root,name) for name in cfg.get('providers',{})}; rows=[]; hp=history_path(repo_root)
    if hp.exists(): rows=[json.loads(l) for l in hp.read_text(encoding='utf-8').splitlines() if l.strip()]
    return {'status':'ok','config':cfg,'budget':load_budget(repo_root),'cache':llm_cache_status(repo_root),'provider_probe':probes,'history_count':len(rows),'recent':rows[-10:]}
