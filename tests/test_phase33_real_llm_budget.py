from pathlib import Path
from uacos.ops.packaging import bootstrap
from uacos.llm.real_providers import init_real_llm, load_real_config, set_allowed_real_run, set_provider
from uacos.token.budget_guard import set_budget, load_budget, check_budget, consume_tokens
from uacos.runtime.llm33_runner import llm_run_real, llm33_status

def test_budget_guard_blocks_cloud_and_allows_local(tmp_path: Path):
    repo=tmp_path/'repo'; repo.mkdir(); bootstrap(repo); set_budget(repo,max_cloud_tokens=10,max_total_tokens=100000,cloud_only=True)
    assert check_budget(repo,100,'openrouter')['status']=='blocked'
    assert check_budget(repo,100000,'ollama')['status']=='pass'
    consume_tokens(repo,50,'ollama'); assert load_budget(repo)['used_cloud_tokens']==0
    consume_tokens(repo,5,'openrouter'); assert load_budget(repo)['used_cloud_tokens']==5

def test_llm33_config_and_dry_run(tmp_path: Path):
    repo=tmp_path/'repo'; repo.mkdir(); (repo/'app.py').write_text('def value():\n    return 1\n',encoding='utf-8'); bootstrap(repo); init_real_llm(repo,'http://192.168.11.127:11434')
    cfg=load_real_config(repo); assert cfg['providers']['ollama_lan']['base_url']=='http://192.168.11.127:11434'; assert cfg['allowed_real_run'] is False
    dry=llm_run_real(repo,'fix app value',size='small',real=False); assert dry['status']=='dry_run'; assert dry['provider']=='ollama_lan'
    assert 'ollama_lan' in llm33_status(repo)['provider_probe']

def test_real_run_blocked_until_allowed(tmp_path: Path):
    repo=tmp_path/'repo'; repo.mkdir(); (repo/'app.py').write_text('def value():\n    return 1\n',encoding='utf-8'); bootstrap(repo); init_real_llm(repo)
    res=llm_run_real(repo,'fix app value',size='small',real=True); assert res['status']=='blocked'; assert res['reason']=='allowed_real_run_false'
    set_allowed_real_run(repo,True); res2=llm_run_real(repo,'fix app value',size='small',real=False); assert res2['status']=='dry_run'

def test_openrouter_disabled_by_default(tmp_path: Path):
    repo=tmp_path/'repo'; repo.mkdir(); bootstrap(repo); init_real_llm(repo); assert load_real_config(repo)['providers']['openrouter']['enabled'] is False
    set_provider(repo,'openrouter',enabled=True); assert load_real_config(repo)['providers']['openrouter']['enabled'] is True
