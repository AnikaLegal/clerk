import pytest

from microsoft.wrapper import MSGraph


def test_constructor():
    api = MSGraph()
    assert isinstance(api.headers["Authorization"], str)
