"""Explicit read-only research; private identifiers/credentials are not search queries."""
import re

def public_query(value):
    if not isinstance(value,str):raise ValueError('invalid_query')
    value=' '.join(value.split())
    if not 2<=len(value)<=80:raise ValueError('invalid_query_length')
    if re.search(r'://|[\w.+-]+@[\w.-]+\.[a-z]{2,}|\b\d{6,}\b|\b(?:sk-[\w-]+|Bearer\s+)|(?:token|cookie|password|api.?key)\s*[:=]',value,re.I):raise ValueError('private_query_rejected')
    return value
