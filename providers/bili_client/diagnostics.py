"""Redact legacy API diagnostics before they reach AstrBot's shared log."""
import re
from astrbot.api import logger as backend
from ..xhh_client.security import redact_log_text

BILI_SECRET = re.compile(r'(?i)\b(SESSDATA|BILI_JCT|DedeUserID|buvid3|buvid4|AC_TIME_VALUE|REFRESH_TOKEN)(\s*[:=]\s*)([^\s,;\}\]]+)')


def safe_text(value):
    return BILI_SECRET.sub(r'\1\2[REDACTED]', redact_log_text(str(value)))[:4000]


class Diagnostics:
    def __init__(self, target=backend):
        self.target=target
    def _emit(self,level,message,*args,**kwargs):
        try:text=str(message)%args if args else str(message)
        except (TypeError,ValueError):text='invalid_diagnostic_format'
        # Raw exception traces can contain request/cookie objects; emit sanitized text only.
        getattr(self.target,level)(safe_text(text))
    def debug(self,*args,**kwargs):self._emit('debug',*args,**kwargs)
    def info(self,*args,**kwargs):self._emit('info',*args,**kwargs)
    def warning(self,*args,**kwargs):self._emit('warning',*args,**kwargs)
    def error(self,*args,**kwargs):self._emit('error',*args,**kwargs)
    def exception(self,*args,**kwargs):self._emit('error',*args,**kwargs)


logger=Diagnostics()
