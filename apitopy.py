from functools import partial
try:
    from urllib.parse import urlencode
except:
    from urllib import urlencode

import requests
from supermutes.dot import dotify


class HttpStatusError(Exception):
    pass


class HttpNotFoundError(HttpStatusError):
    pass


HTTP_ERROR_MAP = {
    404: HttpNotFoundError,
}
HTTP_VERBS = ['GET', 'POST', 'DELETE', 'PUT', 'PATCH', 'HEAD', 'OPTIONS']


def _validate(response):
    """
    Verify the status code of the response and raise exception on codes > 400.
    """
    message = 'HTTP Status: {0}'.format(response.status_code)
    if response.status_code >= 400:
        print(message)
        exception_cls = HTTP_ERROR_MAP.get(response.status_code,
                                           HttpStatusError)
        raise exception_cls(message)
    return response


class EndPoint(object):
    """
    A potential end point of an API, where we can get JSON data from.

    An instance of `EndPoint` is a callable that upon invocation performs
    a GET request. Any kwargs passed in to the call will be used to build
    a query string.
    """

    def __init__(self, api, path, suffix=''):
        self.api = api
        self.path = path
        self.suffix = suffix

    def __getitem__(self, item):
        return EndPoint(self.api,
                        '/'.join([self.path, str(item)]),
                        self.suffix)

    def __getattr__(self, attr):
        if attr in HTTP_VERBS:
            return partial(self._http, attr)
        return self[attr]

    def __call__(self, **kwargs):
        return self.GET(**kwargs)

    def build_url(self, verb='GET', **kwargs):
        """
        Build a URL from base path, use kwargs to build querystring.

        """
        path = self.path
        # Check whether to ensure trailing slash on POST:
        if self.api.ensure_slash and verb == 'POST' and not path.endswith('/'):
            path = path + '/'
        extra = ''
        if kwargs:
            querystring = urlencode(kwargs)
            extra = '?' + querystring
        return "{0}{1}{2}".format(path, self.suffix, extra)

    def _http(self, verb, data=None, **kwargs):
        url = self.build_url(verb, **kwargs)
        response = self.api._http(verb, url, data=data)
        if response.content:
            return dotify(response.json())
        else:
            return None


class Api(object):
    """
    Main class to interact with an API.

    Provides pythonic access to an arbitrary API.

    >>> api = Api('https://sprint.ly/api/', ('user', 'token'), suffix='.json')
    >>> api.products[9134].people()
    GET https://sprint.ly/api/products/9134/people.json
    >>> api.products['9134'].items(assigned_to=11039)
    GET https://sprint.ly/api/products/9134/items.json?assigned_to=11039

    The returned data is a dictionary that you can also access using dot
    notation:

    >>> all = api.products[9134].people()
    >>> my_email = all[0].email
    """

    def __init__(self, base_url, auth=None, verify_ssl_cert=True,
                 suffix='', verbose=False, ensure_slash=False, headers=None):
        self.ROOT = base_url
        self.auth = auth
        self.verify_ssl_cert = verify_ssl_cert
        self.suffix = suffix
        self.verbose = verbose
        self.ensure_slash = ensure_slash
        self.headers = headers or {}
        self.headers.update({
            'Accept': 'application/json',
        })

    def _http(self, verb, path, **kwargs):
        """
        Perform an HTTP request.

        This will add required authentication and SSL verification arguments.
        """
        url = self.ROOT + path
        if self.verbose:
            print('{0} {1}'.format(verb, url))

        method = getattr(requests, verb.lower())
        response = method(url,
                          auth=self.auth,
                          verify=self.verify_ssl_cert,
                          headers=self.headers,
                          **kwargs)
        return _validate(response)

    def __getattr__(self, attr):
        """
        Any attribute you access will be used as part of the URL path.

        Underscores '_' will be replaced with slashes '/'
        """
        if attr in HTTP_VERBS:
            return partial(self._http, attr)
        path = '/'.join(attr.split('_'))
        return EndPoint(self, path, self.suffix)
