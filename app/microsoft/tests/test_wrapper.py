import pytest

from microsoft.wrapper import MSGraph


def test_constructor():
    api = MSGraph()
    assert api.headers["Authorization"] != None
