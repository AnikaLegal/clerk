import json

import responses

from actionstep.api.base import BaseEndpoint


TEST_URL = "https://example.com/rest/test/"


class TestEndpoint(BaseEndpoint):
    resource = "test"


def _get_endpoint():
    return TestEndpoint(base_url="https://example.com", access_token="access")


def _add_response(method, data, status, suffix=""):
    responses.add(
        method,
        TEST_URL + suffix,
        content_type="application/json",
        body=json.dumps(data),
        status=status,
        match_querystring=True,
    )


def test_endpoint_construction():
    endpoint = _get_endpoint()
    assert endpoint.url == TEST_URL
    assert endpoint.headers == {
        "Content-Type": "application/vnd.api+json",
        "Accept": "application/vnd.api+json",
        "Authorization": "Bearer access",
    }


@responses.activate
def test_create():
    data = {"test": {"id": 1, "value": 12345}}
    _add_response(responses.POST, data, 200)
    endpoint = _get_endpoint()
    result = endpoint.create({"value": 12345})
    assert result == {"id": 1, "value": 12345}


@responses.activate
def test_update():
    data = {"test": {"id": 1, "value": 12345}}
    _add_response(responses.PUT, data, 200, suffix="1")
    endpoint = _get_endpoint()
    result = endpoint.update(1, {"value": 12345})
    assert result == {"id": 1, "value": 12345}


@responses.activate
def test_delete():
    data = ""
    _add_response(responses.DELETE, data, 204, suffix="1")
    endpoint = _get_endpoint()
    result = endpoint.delete(resource_id=1)
    assert result is None


@responses.activate
def test_list__with_single_result():
    data = {"test": {"value": 12345}}
    _add_response(responses.GET, data, 200)
    endpoint = _get_endpoint()
    result = endpoint.list()
    assert result == [{"value": 12345}]


@responses.activate
def test_list__with_no_results():
    data = ""
    _add_response(responses.GET, data, 204)
    endpoint = _get_endpoint()
    result = endpoint.list()
    assert result == []


@responses.activate
def test_list__with_multiple_results():
    data = {
        "test": [{"value": 12345}, {"value": 56789}],
        "meta": {
            "paging": {
                "test": {
                    "recordCount": 2,
                    "pageCount": 1,
                    "page": 1,
                    "pageSize": 50,
                    "prevPage": None,
                    "nextPage": None,
                },
            },
        },
    }
    _add_response(responses.GET, data, 200)
    endpoint = _get_endpoint()
    result = endpoint.list()
    assert result == [{"value": 12345}, {"value": 56789}]


@responses.activate
def test_list__with_pagination():
    page_1 = {
        "test": [{"value": 1}, {"value": 2}],
        "meta": {
            "paging": {
                "test": {
                    "recordCount": 5,
                    "pageCount": 3,
                    "page": 1,
                    "pageSize": 2,
                    "prevPage": None,
                    "nextPage": TEST_URL + "?page=2",
                },
            },
        },
    }
    page_2 = {
        "test": [{"value": 3}, {"value": 4}],
        "meta": {
            "paging": {
                "test": {
                    "recordCount": 5,
                    "pageCount": 3,
                    "page": 2,
                    "pageSize": 2,
                    "prevPage": None,
                    "nextPage": TEST_URL + "?page=3",
                },
            },
        },
    }
    page_3 = {
        "test": [{"value": 5}],
        "meta": {
            "paging": {
                "test": {
                    "recordCount": 5,
                    "pageCount": 3,
                    "page": 3,
                    "pageSize": 2,
                    "prevPage": None,
                    "nextPage": None,
                },
            },
        },
    }
    _add_response(responses.GET, page_1, 200)
    _add_response(responses.GET, page_2, 200, suffix="?page=2")
    _add_response(responses.GET, page_3, 200, suffix="?page=3")
    endpoint = _get_endpoint()
    result = endpoint.list()
    assert result == [
        {"value": 1},
        {"value": 2},
        {"value": 3},
        {"value": 4},
        {"value": 5},
    ]
