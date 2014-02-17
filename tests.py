from mock import Mock, patch
from nose.tools import assert_equal

from apitopy import Api


@patch('apitopy.requests')
def test_api_http_verbs(requests):
    mock_response = Mock(status_code=200)

    api = Api('http://example.com/')

    for verb in ['GET', 'POST', 'DELETE']:
        requests_method = getattr(requests, verb.lower())
        requests_method.return_value = mock_response

        response = getattr(api, verb)('hello')

        assert_equal(response.status_code, 200)
        requests_method.assert_called_with(
            'http://example.com/hello',
            auth=None,
            verify=True,
            headers={'Accept': 'application/json'}
        )


@patch('apitopy.requests')
@patch('apitopy._validate')
def test_api_endpoint(_, requests):
    api = Api('http://example.com/')
    endpoint = api.products[123].items[24]

    assert_equal(endpoint.path, 'products/123/items/24')


@patch('apitopy.requests')
@patch('apitopy._validate')
def test_api_endpoint_get(_, requests):
    api = Api('http://example.com/')
    endpoint = api.people.items[24]

    endpoint(since='today')

    requests.get.assert_called_with(
        'http://example.com/people/items/24?since=today',
        auth=None,
        data=None,
        verify=True,
        headers={'Accept': 'application/json'}
    )
