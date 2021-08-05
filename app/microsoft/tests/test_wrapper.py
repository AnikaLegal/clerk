import pytest

from microsoft.wrapper import MSGraph


def test_constructor():
    api = MSGraph()
    assert isinstance(api.headers["Authorization"], str)


def test_get():
    api = MSGraph()
    resp = api.get(path="users/bugs.bunny@anikalegal.com")
    assert resp.status_code == 200
