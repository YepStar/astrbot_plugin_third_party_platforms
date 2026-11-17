import math
from datetime import datetime
from zoneinfo import ZoneInfo
from .sharing import routes

def score_threshold(config, account, key):
    """An account override wins; global settings are only a readable fallback."""
    for raw in (account.get(key), config.get(key), 8):
        if isinstance(raw, bool) or raw is None:
            continue
        try:
            value = float(raw)
        except (TypeError, ValueError, OverflowError):
            continue
        if math.isfinite(value) and 1 <= value <= 10:
            return value
    return 8.0

class Policy:
    def __init__(self,config,ready=None):self.config=config;self.ready=ready
    def account(self,provider,account):
        if self.ready is not None and not self.ready():raise PermissionError('deployment_not_ready')
        value=self.config.get('platforms',{}).get(provider,{})
        if not self.config.get('enabled',False) or not value.get('enabled',False):raise PermissionError('platform_disabled')
        item=value.get('accounts',{}).get(account)
        if not item or not item.get('enabled',False):raise PermissionError('account_disabled')
        return item
    def permit(self,provider,account,action,evaluation=None):
        item=self.account(provider,account)
        if action=='block_user':
            if item.get('reply',{}).get('dry_run',False) or not any(item.get('safety',{}).get(k) for k in ('auto_block','private_auto_block')):raise PermissionError('blocking_disabled')
            return item
        if action in {'reply','private_reply','comment','dynamic','like','coin','favorite','follow'} and item.get('reply',{}).get('dry_run',False):raise PermissionError('dry_run_enabled')
        if action=='browse' and not item.get('browse',{}).get('browse_enabled',True):raise PermissionError('browsing_disabled')
        if action in {'like','coin','favorite','follow'}:
            rules=item.get('interactions',{})
            if not rules.get(action+'_enabled') or evaluation is None or evaluation.score<rules.get(action+'_min_score',9):raise PermissionError('interaction_score_gate')
            return item
        if action!='browse' and not item.get('actions',{}).get(action,False):raise PermissionError('action_disabled')
        if action=='comment':
            floor=score_threshold(self.config,item,'comment_min_score')
            if evaluation is None or evaluation.score<floor:raise PermissionError('comment_score_gate')
        if action=='owner_share':
            floor=score_threshold(self.config,item,'share_min_score')
            if evaluation is None or not evaluation.recommend or evaluation.score<floor:raise PermissionError('score_gate')
            if not routes(provider,item):raise PermissionError('recipient_unconfigured')
        return item
    def limits(self,provider,account,kind,now):
        item=self.account(provider,account)
        dt=datetime.fromtimestamp(now,ZoneInfo(self.config.get('timezone','Asia/Shanghai')))
        day=dt.date().isoformat();minute=dt.strftime('%Y-%m-%dT%H:%M')
        return [('all',day,int(self.config.get('daily_limit',20))),
                ('minute',minute,int(self.config.get('minute_limit',2))),
                (f'{provider}:{account}:{kind}',day,int(item.get('interactions',{}).get('interaction_daily_limit',2) if kind in {'like','coin','favorite','follow'} else 5 if kind=='block_user' else item.get('daily_limits',{}).get(kind,1)))]
