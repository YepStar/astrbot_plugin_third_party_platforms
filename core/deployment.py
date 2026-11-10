"""Persisted deployment verification plus live coexistence checks; fail closed."""
LEGACY=('astrbot_plugin_bilibili_ai_bot','astrbot_plugin_xiaoheihe_adapter')

def checks(host):
    proof=host.store.setting('deployment',{})
    result={'migration_verified':proof.get('schema')==1 and proof.get('verified') is True,
            'model_configured':bool(host.config.get('provider_id')),
            'accounts_configured':any(a.get('enabled') for p in host.config.get('platforms',{}).values() for a in p.get('accounts',{}).values()),
            'legacy_plugins_stopped':False,'legacy_transport_stopped':False}
    try:
        result['legacy_plugins_stopped']=all((item:=host.context.get_registered_star(name)) is None or getattr(item,'activated',True) is False for name in LEGACY)
        root=host.context.get_config()
        result['legacy_transport_stopped']=not any(p.get('type')=='xiaoheihe' and p.get('enable',False) for p in root.get('platform',[]))
    except (AttributeError,TypeError,RuntimeError):pass
    return result
