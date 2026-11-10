from datetime import datetime
from zoneinfo import ZoneInfo
from .sharing import routes

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
        if action in {'reply','private_reply','comment','dynamic'} and item.get('reply',{}).get('dry_run',False):raise PermissionError('dry_run_enabled')
        if action!='browse' and not item.get('actions',{}).get(action,False):raise PermissionError('action_disabled')
        if action=='comment':
            floor=max(float(self.config.get('comment_min_score',8)),float(item.get('comment_min_score',0)))
            if evaluation is None or evaluation.score<floor:raise PermissionError('comment_score_gate')
        if action=='owner_share':
            floor=max(float(self.config.get('share_min_score',8)),float(item.get('share_min_score',0)))
            if evaluation is None or not evaluation.recommend or evaluation.score<floor:raise PermissionError('score_gate')
            if not routes(provider,item):raise PermissionError('recipient_unconfigured')
        return item
    def limits(self,provider,account,kind,now):
        item=self.account(provider,account)
        dt=datetime.fromtimestamp(now,ZoneInfo(self.config.get('timezone','Asia/Shanghai')))
        day=dt.date().isoformat();minute=dt.strftime('%Y-%m-%dT%H:%M')
        return [('all',day,int(self.config.get('daily_limit',20))),
                ('minute',minute,int(self.config.get('minute_limit',2))),
                (f'{provider}:{account}:{kind}',day,int(item.get('daily_limits',{}).get(kind,1)))]
