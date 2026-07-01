from __future__ import annotations
import json, urllib.request, os
from pathlib import Path
from datetime import datetime, timezone
from uacos.config import uacos_dir
from uacos.llm.hardened import estimate_tokens
from uacos.token.budget_guard import check_budget, consume_tokens

def utcnow(): return datetime.now(timezone.utc).isoformat()
def real_config_path(repo_root: Path) -> Path:
    p=uacos_dir(repo_root); p.mkdir(parents=True, exist_ok=True); return p/'llm_real_config.json'
DEFAULT_REAL_CONFIG={"version":1,"allowed_real_run":False,"default_size":"small","providers":{"ollama_lan":{"type":"ollama","base_url":"http://192.168.11.127:11434","enabled":True,"timeout_sec":180,"models":{"tiny":"qwen2.5-coder:7b","small":"qwen2.5-coder:7b","medium":"qwen3:30b-architect","large":"qwen3.6:35b","critical":"qwen3.6:35b"}},"ollama_local":{"type":"ollama","base_url":"http://localhost:11434","enabled":True,"timeout_sec":180,"models":{"tiny":"qwen2.5-coder:7b","small":"qwen2.5-coder:7b","medium":"qwen3:30b-architect","large":"qwen3.6:35b","critical":"qwen3.6:35b"}},"openrouter":{"type":"openrouter","base_url":"https://openrouter.ai/api/v1","api_key_env":"OPENROUTER_API_KEY","enabled":False,"timeout_sec":180,"models":{"tiny":"openai/gpt-4o-mini","small":"openai/gpt-4o-mini","medium":"anthropic/claude-3.5-sonnet","large":"anthropic/claude-3.5-sonnet","critical":"anthropic/claude-3.5-sonnet"}}},"routing":{"tiny":["ollama_lan","ollama_local"],"small":["ollama_lan","ollama_local"],"medium":["ollama_lan","ollama_local","openrouter"],"large":["ollama_lan","ollama_local","openrouter"],"critical":["ollama_lan","ollama_local","openrouter"]},"updated_at":None}
def load_real_config(repo_root):
    p=real_config_path(repo_root)
    if not p.exists(): save_real_config(repo_root, DEFAULT_REAL_CONFIG.copy())
    return json.loads(p.read_text(encoding='utf-8'))
def save_real_config(repo_root,cfg):
    cfg=dict(cfg); cfg['updated_at']=utcnow(); p=real_config_path(repo_root); p.write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf-8'); return {'status':'ok','config_file':str(p),'config':cfg}
def init_real_llm(repo_root, ollama_lan='http://192.168.11.127:11434'):
    cfg=load_real_config(repo_root); cfg['providers']['ollama_lan']['base_url']=ollama_lan.rstrip('/'); return save_real_config(repo_root,cfg)
def set_allowed_real_run(repo_root, allowed):
    cfg=load_real_config(repo_root); cfg['allowed_real_run']=bool(allowed); return save_real_config(repo_root,cfg)
def set_provider(repo_root, provider, enabled=None, base_url=None, api_key_env=None):
    cfg=load_real_config(repo_root)
    if provider not in cfg['providers']: raise ValueError(f'unknown_provider:{provider}')
    p=cfg['providers'][provider]
    if enabled is not None: p['enabled']=bool(enabled)
    if base_url: p['base_url']=base_url.rstrip('/')
    if api_key_env: p['api_key_env']=api_key_env
    return save_real_config(repo_root,cfg)
def route_providers(cfg,size):
    out=[]; size=size or cfg.get('default_size','small')
    for name in cfg.get('routing',{}).get(size,[]):
        pcfg=cfg['providers'].get(name)
        if pcfg and pcfg.get('enabled',False): out.append((name, pcfg.get('models',{}).get(size) or pcfg.get('models',{}).get('small'), pcfg))
    return out
def _post_json(url,payload,headers=None,timeout=180):
    req=urllib.request.Request(url,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json',**(headers or {})},method='POST')
    with urllib.request.urlopen(req,timeout=timeout) as resp: return json.loads(resp.read().decode())
def call_ollama(base_url,model,prompt,timeout=180):
    data=_post_json(base_url.rstrip('/')+'/api/generate',{'model':model,'prompt':prompt,'stream':False},timeout=timeout); content=data.get('response',''); total=int((data.get('prompt_eval_count') or estimate_tokens(prompt))+(data.get('eval_count') or estimate_tokens(content))); return {'status':'ok','content':content,'usage':{'total_tokens':total},'raw':data}
def call_openrouter(base_url,api_key,model,prompt,timeout=180):
    data=_post_json(base_url.rstrip('/')+'/chat/completions',{'model':model,'messages':[{'role':'user','content':prompt}],'temperature':0},headers={'Authorization':f'Bearer {api_key}'},timeout=timeout); content=data.get('choices',[{}])[0].get('message',{}).get('content',''); usage=data.get('usage') or {}; usage.setdefault('total_tokens',estimate_tokens(prompt)+estimate_tokens(content)); return {'status':'ok','content':content,'usage':usage,'raw':data}
def call_provider(repo_root,provider_name,model,pcfg,prompt,real=False):
    ptype=pcfg.get('type'); est=estimate_tokens(prompt)+1024; budget=check_budget(repo_root,est,ptype)
    if budget['status']!='pass': return {'status':'blocked','provider':provider_name,'model':model,'reason':budget['reason'],'budget':budget}
    if not real: return {'status':'dry_run','provider':provider_name,'model':model,'estimated_tokens':est}
    if ptype=='ollama': result=call_ollama(pcfg['base_url'],model,prompt,timeout=int(pcfg.get('timeout_sec',180)))
    elif ptype=='openrouter':
        key=os.environ.get(pcfg.get('api_key_env','OPENROUTER_API_KEY'))
        if not key: return {'status':'error','provider':provider_name,'model':model,'error':'missing_openrouter_api_key_env'}
        result=call_openrouter(pcfg['base_url'],key,model,prompt,timeout=int(pcfg.get('timeout_sec',180)))
    else: return {'status':'error','provider':provider_name,'model':model,'error':f'unsupported_provider_type:{ptype}'}
    tokens=int((result.get('usage') or {}).get('total_tokens') or est); consume=consume_tokens(repo_root,tokens,ptype); return {'status':'ok','provider':provider_name,'provider_type':ptype,'model':model,'content':result.get('content',''),'usage':result.get('usage',{}),'budget_after':consume.get('budget')}
def run_with_fallback(repo_root,prompt,size='small',real=False):
    cfg=load_real_config(repo_root)
    if real and not cfg.get('allowed_real_run',False): return {'status':'blocked','reason':'allowed_real_run_false','hint':'run: uacos llm33-allow-real --repo . --yes'}
    attempts=[]
    for name,model,pcfg in route_providers(cfg,size):
        res=call_provider(repo_root,name,model,pcfg,prompt,real=real); attempts.append({k:v for k,v in res.items() if k not in {'content','raw'}})
        if res.get('status') in {'ok','dry_run'}: res['attempts']=attempts; return res
        if res.get('status')=='blocked': return {'status':'blocked','reason':res.get('reason'),'attempts':attempts,'blocked_provider':name}
    return {'status':'failed','reason':'all_providers_failed','attempts':attempts}
def provider_probe(repo_root,provider='ollama_lan'):
    cfg=load_real_config(repo_root); pcfg=cfg['providers'].get(provider)
    if not pcfg: return {'status':'fail','reason':'provider_not_found'}
    if pcfg.get('type')=='ollama':
        try:
            with urllib.request.urlopen(urllib.request.Request(pcfg['base_url'].rstrip('/')+'/api/tags',method='GET'),timeout=10) as resp: data=json.loads(resp.read().decode())
            return {'status':'ok','provider':provider,'models':[m.get('name') for m in data.get('models',[])],'base_url':pcfg['base_url']}
        except Exception as exc: return {'status':'fail','provider':provider,'error':{'type':type(exc).__name__,'message':str(exc)},'base_url':pcfg.get('base_url')}
    return {'status':'ok','provider':provider,'type':pcfg.get('type'),'enabled':pcfg.get('enabled')}
