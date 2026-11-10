from __future__ import annotations
from dataclasses import dataclass, field
from typing import Protocol

@dataclass(frozen=True)
class Content:
    provider: str
    account: str
    external_id: str
    url: str
    title: str
    text: str
    author_id: str = ''
    modality: str = 'text'
    metadata: dict = field(default_factory=dict)

    @property
    def key(self):return f'{self.provider}:{self.account}:{self.external_id}'

@dataclass(frozen=True)
class Evaluation:
    score: float
    reason: str
    evidence: str
    recommend: bool = False
    interests: tuple[str, ...] = ()

    def __post_init__(self):
        import math
        if type(self.score) not in (int,float) or not math.isfinite(self.score) or not 1<=self.score<=10:
            raise ValueError('invalid_score')
        if not self.reason.strip() or not self.evidence.strip():raise ValueError('missing_evidence')
        if type(self.recommend) is not bool:raise ValueError('invalid_recommendation')

@dataclass(frozen=True)
class Receipt:
    state: str
    external_id: str = ''
    code: str = ''
    def __post_init__(self):
        if self.state not in {'succeeded','failed','unknown'}:raise ValueError('invalid_receipt')

class Provider(Protocol):
    id: str
    capabilities: frozenset[str]
    async def status(self, account: str) -> dict: ...
    async def browse(self, account: str, options: dict) -> list[Content]: ...
    async def execute(self, account: str, action: str, params: dict, key: str) -> Receipt: ...
    async def close(self) -> None: ...

class Registry:
    def __init__(self):self.providers={};self.manifests={}
    def register(self, provider, definition=None):
        if not provider.id or provider.id in self.providers:raise ValueError('duplicate_provider')
        self.providers[provider.id]=provider
        self.manifests[provider.id]=definition or {'api':1,'name':provider.id,'fields':{}}
    def get(self, key, capability=None):
        provider=self.providers[key]
        if capability and capability not in provider.capabilities:raise ValueError('unsupported_capability')
        return provider

@dataclass(frozen=True)
class Incoming:
    provider: str
    account: str
    stream: str
    external_id: str
    actor_id: str
    text: str
    created: float
    route: dict
    actor_verified: bool = False
    explicit: bool = True
    author_id: str = ''
    source_text: str = ''
    context: dict = field(default_factory=dict)
    @property
    def key(self):return f'{self.provider}:{self.account}:{self.stream}:{self.external_id}'
