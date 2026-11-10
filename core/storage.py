"""Scoped diagnostics and body retention; never remove action/dedupe/quota ledgers."""
import time
TABLES=('tasks','actions','observations','inbox','read_content')
def status(store,provider):
    with store.connect() as db:
        counts={name:db.execute(f'SELECT COUNT(*) FROM {name} WHERE provider=?',(provider,)).fetchone()[0] for name in TABLES}
    files=[store.path,store.path.with_name(store.path.name+'-wal'),store.path.with_name(store.path.name+'-shm')]
    return {'database_bytes':sum(p.stat().st_size for p in files if p.exists()),'database_shared':True,'counts':counts,'last_cleanup':store.setting('cleanup:'+provider,None),'retention_days':store.setting('retention:'+provider,30),'protected':['发送回执与幂等键','配额账本','已读去重','日程历史','偏好学习','待处理事件','记忆发件箱']}
def preview(store,provider,days):
    if type(days)is not int or not 7<=days<=3650:raise ValueError('保留天数应在 7–3650 之间')
    cutoff=time.time()-days*86400
    with store.connect() as db:
        count=db.execute("SELECT COUNT(*) FROM inbox WHERE provider=? AND state IN ('succeeded','ignored','failed') AND payload!='{}' AND json_extract(payload,'$.created')<?",(provider,cutoff)).fetchone()[0]
    return {'body_count':count,'retention_days':days,'cutoff':cutoff,'note':'仅压缩到期且已结束的收件事件正文；凭据、发送回执、去重键、配额、日程和记忆均保留。'}
def cleanup(store,provider,days):
    result=preview(store,provider,days)
    with store.connect() as db:
        removed=db.execute("UPDATE inbox SET payload='{}' WHERE provider=? AND state IN ('succeeded','ignored','failed') AND payload!='{}' AND json_extract(payload,'$.created')<?",(provider,result['cutoff'])).rowcount
    store.set_setting('cleanup:'+provider,time.time());store.set_setting('retention:'+provider,days)
    return {**result,'pruned_bodies':removed}
