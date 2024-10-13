from mock import Mock, patch

from apitopy import Api


@patch("apitopy.requests")
def test_api_http_verbs(requests):
    mock_response = Mock(status_code=200, content={"key": "value"})

    api = Api("http://example.com/")

    for verb in ["GET", "POST", "DELETE"]:
        requests_method = getattr(requests, verb.lower())
        requests_method.return_value = mock_response

        response = getattr(api, verb)("hello")

        assert response.status_code == 200
        requests_method.assert_called_with(
            "http://example.com/hello",
            auth=None,
            verify=True,
            headers={"Accept": "application/json"},
        )


@patch("apitopy.requests")
@patch("apitopy._validate")
def test_api_endpoint(_, requests):
    api = Api("http://example.com/")
    endpoint = api.products[123].items[24]

    assert endpoint.path == "products/123/items/24"


@patch("apitopy.requests.get")
def test_api_endpoint_get(requests_get):
    mock_response = Mock(status_code=200, json=Mock(return_value={"key": "value"}))
    requests_get.return_value = mock_response

    api = Api("http://example.com/")
    result = api.people.items[24](since="today")

    requests_get.assert_called_with(
        "http://example.com/people/items/24?since=today",
        auth=None,
        data=None,
        json=None,
        verify=True,
        headers={"Accept": "application/json"},
    )
    assert result.key == "value"


def test_api_endpoint_build_url_with_querystring():
    api = Api("http://example.com/")
    endpoint = api.people.items[24]

    result = endpoint.build_url(hello="dolly")

    assert result == "people/items/24?hello=dolly"
