from __future__ import annotations

import pytest

from astrbot_plugin_third_party_platforms.providers.xhh_client.security import (
    SecurityError,
    redact_data,
    redact_log_text,
    redact_text,
    sanitize_reply_text,
    validate_public_https_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "http://example.com/a.png",
        "file:///etc/passwd",
        "https://127.0.0.1/a.png",
        "https://10.0.0.1/a.png",
        "https://user:pw@example.com/a.png",
    ],
)
def test_ssrf_and_local_url_protection(url: str) -> None:
    with pytest.raises(SecurityError):
        validate_public_https_url(url)


def test_public_https_is_allowed() -> None:
    assert validate_public_https_url("https://cdn.example.com/a.png") == (
        "https://cdn.example.com/a.png"
    )


def test_sensitive_log_redaction() -> None:
    assert "secret-value" not in redact_text("Authorization: Bearer secret-value")
    assert "device-123" not in redact_text(
        "https://example.test/path?device_id=device-123&token=token-456"
    )
    diagnostic = redact_log_text(
        "failed https://user:password@example.test/image.png?signature=private#fragment"
    )
    assert "user:password" not in diagnostic
    assert "signature=private" not in diagnostic
    assert "fragment" not in diagnostic
    assert "https://example.test/image.png?[REDACTED]#[REDACTED]" in diagnostic
    assert redact_data({"cookie": "secret", "nested": {"token": "secret"}}) == {
        "cookie": "[REDACTED]",
        "nested": {"token": "[REDACTED]"},
    }


def test_reply_cleanup_and_length() -> None:
    result = sanitize_reply_text("hello\n```tool\nsecret\n```\nworld", 8)
    assert result == "hello\nwo"
    with pytest.raises(SecurityError, match="空回复"):
        sanitize_reply_text("```debug\nx\n```", 100)

@pytest.mark.parametrize('raw,expected', [
    ('<quote id="982891825"/>大概是同样的格式串了。', '大概是同样的格式串了。'),
    ("<quote id='msgxhh_reply_4448015201_982888224'/>配饰只改样子。", '配饰只改样子。'),
    ('<QUOTE id = "123" />正文</QUOTE>', '正文'),
    ('前文<quote id="1"/>后文', '前文后文'),
    ('<mention id="123"/>你好</mention>', '你好'),
    ('&lt;quote id=&quot;123&quot;/&gt;你好', '你好'),
    ('&amp;lt;quote id=&amp;quot;123&amp;quot;/&amp;gt;你好', '你好'),
    ('我引用了“这句话”，x < 3，正文保留 <b>重点</b>。', '我引用了“这句话”，x < 3，正文保留 <b>重点</b>。'),
])
def test_public_comments_never_contain_transport_control_tags(raw, expected):
    assert sanitize_reply_text(raw, 500) == expected
    assert sanitize_reply_text(raw, 2) == expected[:2]

@pytest.mark.parametrize('raw', ['<quote id="123"/>', '<quote id="1"/><mention id="2"/>'])
def test_control_tags_only_are_empty_not_public_comments(raw):
    with pytest.raises(SecurityError, match='空回复'):
        sanitize_reply_text(raw, 500)
