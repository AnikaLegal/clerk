from types import SimpleNamespace

from emails.utils.size import base64_size, format_size, get_email_payload_size


def _attachment(size):
    return SimpleNamespace(file=SimpleNamespace(size=size))


def test_base64_size():
    # base64 encodes 3 bytes into 4, padding partial groups.
    assert base64_size(0) == 0
    assert base64_size(1) == 4
    assert base64_size(3) == 4
    assert base64_size(4) == 8
    assert base64_size(6) == 8


def test_get_email_payload_size_counts_body_and_encoded_attachments():
    size = get_email_payload_size("ab", "cde", [_attachment(3), _attachment(6)])
    # body: 2 + 3 bytes; attachments: base64_size(3)=4, base64_size(6)=8
    assert size == 2 + 3 + 4 + 8


def test_get_email_payload_size_handles_no_body():
    assert get_email_payload_size(None, None, []) == 0


def test_format_size():
    assert format_size(0) == "0.0MB"
    assert format_size(29 * 1024 * 1024) == "29.0MB"
    assert format_size(int(21.7 * 1024 * 1024)) == "21.7MB"


def test_get_email_payload_size_accounts_for_base64_inflation():
    # A raw payload under 30MB can exceed 30MB once base64 encoded: this is the
    # bug the old per-file `size / 1024 / 1024 > 30` check missed.
    raw = 25 * 1024 * 1024
    assert raw < 30 * 1024 * 1024
    assert get_email_payload_size("", "", [_attachment(raw)]) > 30 * 1024 * 1024
