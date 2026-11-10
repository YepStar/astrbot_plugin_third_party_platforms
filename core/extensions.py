"""Version-one provider manifests and public (non-credential) option validation."""
import math
import re
from ..providers.xhh_client.security import SENSITIVE_KEY_RE

CAPABILITIES = {'browse', 'search', 'reply', 'private_reply', 'comment', 'dynamic', 'owner_share', 'listen'}
TYPES = {'string', 'int', 'float', 'bool', 'list'}


def manifest(provider, value=None):
    value = dict(value or {})
    if not re.fullmatch(r'[a-z][a-z0-9_]{0,63}', provider.id):
        raise ValueError('invalid_provider_id')
    if value.keys() - {'api', 'name', 'fields'} or value.get('api', 1) != 1:
        raise ValueError('unsupported_provider_manifest')
    if not set(provider.capabilities) <= CAPABILITIES:
        raise ValueError('unknown_provider_capability')
    for name in ['status', 'close'] + (['browse'] if 'browse' in provider.capabilities else []) + (['search'] if 'search' in provider.capabilities else []) + (['execute'] if set(provider.capabilities)-{'browse','search','owner_share'} else []):
        if not callable(getattr(provider, name, None)):
            raise ValueError('missing_provider_method')
    name = value.get('name', provider.id)
    fields = value.get('fields', {})
    if not isinstance(name, str) or not 1 <= len(name) <= 80 or not isinstance(fields, dict) or len(fields) > 32:
        raise ValueError('invalid_provider_manifest')
    for key, field in fields.items():
        if not re.fullmatch(r'[a-z][a-z0-9_]{0,63}', key) or SENSITIVE_KEY_RE.search(key):
            raise ValueError('credential_not_public_option')
        if not isinstance(field, dict) or field.keys() - {'type', 'description', 'default', 'min', 'max'} or field.get('type') not in TYPES:
            raise ValueError('invalid_provider_field')
        if not isinstance(field.get('description', key), str) or len(field.get('description', key)) > 200:
            raise ValueError('invalid_field_description')
        for bound in ['min', 'max']:
            if bound in field and (type(field[bound]) not in (int, float) or not math.isfinite(field[bound])):
                raise ValueError('invalid_option_bound')
    result = {'api': 1, 'name': name, 'fields': fields}
    options(result, {})  # Validate defaults before exposing the extension.
    return result


def options(definition, values, previous=None):
    fields = definition['fields']
    if not isinstance(values, dict) or values.keys() - fields.keys():
        raise ValueError('invalid_provider_options')
    result = {}
    for key, field in fields.items():
        value = values.get(key, (previous or {}).get(key, field.get('default')))
        kind = field['type']
        if value is None:
            continue
        if kind == 'string' and (not isinstance(value, str) or len(value) > 2000):
            raise ValueError('invalid_provider_option')
        if kind == 'bool' and type(value) is not bool:
            raise ValueError('invalid_provider_option')
        if kind in {'int', 'float'}:
            if type(value) not in (int, float) or not math.isfinite(value) or (kind == 'int' and int(value) != value):
                raise ValueError('invalid_provider_option')
            if not field.get('min', -1e9) <= value <= field.get('max', 1e9):
                raise ValueError('provider_option_out_of_range')
        if kind == 'list' and (not isinstance(value, list) or len(value) > 200 or any(not isinstance(v, str) or len(v) > 100 for v in value)):
            raise ValueError('invalid_provider_option')
        result[key] = value
    return result
