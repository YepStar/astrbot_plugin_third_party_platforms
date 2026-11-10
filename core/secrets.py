"""Opaque per-account credentials; never included in public state."""
from pathlib import Path
import json,re,os,tempfile

class SecretStore:
    def __init__(self,root):
        self.root=Path(root);self.root.mkdir(parents=True,exist_ok=True);self.root.chmod(0o700)
    def path(self,provider,account):
        for value in (provider,account):
            if not re.fullmatch(r'[a-zA-Z0-9_-]{1,64}',value):raise ValueError('invalid_account_id')
        return self.root/f'{provider}--{account}.json'
    def read(self,provider,account):
        p=self.path(provider,account)
        if not p.exists():return {}
        if p.is_symlink():raise ValueError('credential_symlink')
        value=json.loads(p.read_text())
        if not isinstance(value,dict):raise ValueError('invalid_credentials')
        return value
    def write(self,provider,account,value):
        if not isinstance(value,dict):raise ValueError('invalid_credentials')
        p=self.path(provider,account)
        fd,tmp=tempfile.mkstemp(dir=self.root,prefix='.pending-')
        try:
            with os.fdopen(fd,'w') as stream:json.dump(value,stream)
            os.replace(tmp,p)
        finally:
            Path(tmp).unlink(missing_ok=True)
    def delete(self,provider,account):self.path(provider,account).unlink(missing_ok=True)
