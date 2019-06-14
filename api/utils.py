import time

from urllib import parse

from django.utils.encoding import force_str


def replace_query_params(url, params: dict):
    """
    Given a URL and a key/val pair, set or replace an item in the query
    parameters of the URL, and return the new URL.
    """
    (scheme, netloc, path, query, fragment) = parse.urlsplit(force_str(url))
    query_dict = parse.parse_qs(query, keep_blank_values=True)
    for key, val in params.items():
        query_dict[force_str(key)] = [force_str(val)]
    query = parse.urlencode(sorted(list(query_dict.items())), doseq=True)
    return parse.urlunsplit((scheme, netloc, path, query, fragment))


def replace_query_param(url, key, val):
    return replace_query_params(url, {key: val})


def replace_query_path(url, new_path):
    (scheme, netloc, path, query, fragment) = parse.urlsplit(force_str(url))
    return parse.urlunsplit((scheme, netloc, new_path, '', ''))


class HttpHeaders:
    HTTP_PREFIX = 'HTTP_'
    # PEP 333 gives two headers which aren't prepended with HTTP_.
    UNPREFIXED_HEADERS = {'CONTENT_TYPE', 'CONTENT_LENGTH'}

    def __init__(self, environ):
        self.headers = {}
        for header, value in environ.items():
            name = self.parse_header_name(header)
            if name:
                self.headers[name] = value

    @classmethod
    def parse_header_name(cls, header):
        if header.startswith(cls.HTTP_PREFIX):
            header = header[len(cls.HTTP_PREFIX):]
        elif header not in cls.UNPREFIXED_HEADERS:
            return None
        return header.replace('_', '-').title()


def http_headers(request):
    if hasattr(request, '_http_headers'):
        return request._http_headers.headers
    header_parser = HttpHeaders(request.META)
    request._http_headers = header_parser
    return header_parser.headers


def timeit(func):
    def call(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(func.__name__, end - start, *args, *kwargs.items())
        return result

    return call
