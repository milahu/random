#!/usr/bin/env python3

# nix-shell -p python3.pkgs.{requests,aiohttp,werkzeug}


import sys
#from io import BytesIO
#from urllib3 import HTTPResponse
import email
import http.client

# https://docs.python.org/3/library/http.client.html
from http.client import parse_headers


# html != http ...
#def parse_html_header(header):
def parse_http_headers(header_bytes):

    # https://stackoverflow.com/a/52418392/10440128

    '''
    # see also "def _read_status" in
    # https://github.com/python/cpython/raw/3.12/Lib/http/client.py
    redirects = []
    while True:
        header, body = header_bytes.split(b"\r\n\r\n", 1)
        if body[:4] == b"HTTP": # TODO verify false positives
            redirects.append(header)
            header_bytes = body
        else:
            break
    '''

    #f = BytesIO(header)
    # read one line for HTTP/2 STATUSCODE MESSAGE
    #requestline = f.readline().split(b" ")
    requestline, header_bytes = header_bytes.split(b"\r\n", 1)
    #protocol, status = requestline[:2]

    #headers = parse_headers(f) # http.client.HTTPMessage

    #parser = email.parser.Parser(_class=http.client.HTTPMessage)
    parser = email.parser.Parser()

    headers = parser.parsestr(header_bytes.decode('iso-8859-1'))

    hdict = {}

    for key, value in headers.items():
        key = key.lower()
        if key in hdict:
            current_value = hdict.get(key)
            if isinstance(current_value, list):
                current_value.append(value)
            else:
                hdict[key] = [current_value, value]
        else:
            hdict[key] = value

    return hdict



header_bytes = (
    b'HTTP/2 302 \r\n'
    b'server: ddos-guard\r\n'
    b'server: ddos-guard 2\r\n'
    b'server: ddos-guard 3\r\n'
    b'date: Mon, 10 Jun 2024 17:42:58 GMT\r\n'
    # https://stackoverflow.com/questions/4400678/what-character-encoding-should-i-use-for-a-http-header
    b'test-rfc2047: =?UTF-8?Q?=E2=9C=B0?=\r\n'
    b'content-length: 0\r\n'
    b'location: https://www857.ucdn.to:183/d/xxx/yyy (Ungek\xfcrzt).rar\r\n'
    b'access-control-allow-origin: *\r\n'
    b'access-control-allow-headers: X-Requested-With\r\n'
    b'access-control-allow-methods: GET,POST,OPTIONS\r\n'
    b'\r\n'
)

headers = parse_http_headers(header_bytes)

"""
print("headers", repr(headers))
print("headers", dir(headers))
print("headers", headers.items())
"""

for key in headers:
    print("header", key, headers[key])

assert headers["location"] == "https://www857.ucdn.to:183/d/xxx/yyy (Ungekürzt).rar"


'''
    header = to_str(header)

    hdict = {}
    _re = r"[ ]*(?P<key>.+?)[ ]*:[ ]*(?P<value>.+?)[ ]*\r?\n"

    for key, value in re.findall(_re, header):
        key = key.lower()
        if key in hdict:
            current_value = hdict.get(key)
            if isinstance(current_value, list):
                current_value.append(value)
            else:
                hdict[key] = [current_value, value]
        else:
            hdict[key] = value

    return hdict
'''



if 0:
    # https://stackoverflow.com/a/52418392/10440128

    import sys
    #from io import BytesIO
    #from urllib3 import HTTPResponse
    import email
    import http.client

    # https://docs.python.org/3/library/http.client.html
    from http.client import parse_headers

    #rawresponse = sys.stdin.read().encode("utf8")
    rawresponse = header_bytes
    redirects = []

    # see also "def _read_status" in
    # https://github.com/python/cpython/raw/3.12/Lib/http/client.py
    while True:
        header, body = rawresponse.split(b"\r\n\r\n", 1)
        if body[:4] == b"HTTP": # TODO verify false positives
            redirects.append(header)
            rawresponse = body
        else:
            break

    #f = BytesIO(header)
    # read one line for HTTP/2 STATUSCODE MESSAGE
    #requestline = f.readline().split(b" ")
    requestline, header = header.split(b"\r\n", 1)
    protocol, status = requestline[:2]

    #headers = parse_headers(f) # http.client.HTTPMessage
    headers = email.parser.Parser(_class=http.client.HTTPMessage).parsestr(header.decode('iso-8859-1'))

    print("headers", repr(headers))

    for key in headers:
        print("header", key, headers[key])

    assert headers["location"] == "https://www857.ucdn.to:183/d/xxx/yyy (Ungekürzt).rar"



    # ValueError: too many values to unpack (expected 2)
    """
    resp = HTTPResponse(body, headers=headers)
    resp.status = int(status)

    print("headers")
    print(resp.headers)

    print("redirects")
    print(redirects)
    """

if 0:
    import http.client
    import email
    # also used by http.client.parse_headers
    res = email.parser.Parser(_class=http.client.HTTPMessage).parsestr(header_bytes.decode('iso-8859-1'))
    #res = email.parser.Parser().parsestr(header_bytes.decode('iso-8859-1'))
    print(repr(res), res)

if 0:
    import aiohttp.http_parser
    p = aiohttp.http_parser.HttpResponseParserPy()
    # Bad status line 'HTTP/2 302 '
    p.feed_data(header_bytes)
    p.feed_eof()
    res = p.parse_headers()
    print(res)

if 0:
    import aiohttp.http_parser
    p = aiohttp.http_parser.HttpResponseParser(
        protocol=None,
        loop=None,
        limit=65536,
        #max_line_size=8190,
        #max_headers=32768,
        #max_field_size=8190,
    )

    # remove the status line
    # no: Expected HTTP/
    #assert header_bytes.startswith(b"HTTP")
    #header_bytes = header_bytes.split(b"\r\n", 1)[1]

    # Expected dot: b'HTTP/2 302 '
    p.feed_data(header_bytes)

    p.feed_eof()
    res = p.parse_headers()
    print(res)

if 0:
    # https://pypi.org/project/http-parser/

    # try to import C parser then fallback in pure python parser.
    try:
        from http_parser.parser import HttpParser
    except ImportError:
        from http_parser.pyparser import HttpParser

    p = HttpParser()

    data = header_bytes

    recved = len(data)
    nparsed = p.execute(data, recved)

    print("recved ", recved) # 283
    print("nparsed", nparsed) # 6 # wtf?

    #assert nparsed == recved # fixme

    #if p.is_headers_complete():
    if 1:
        print(p.get_headers())

if 0:
    # used by requests/src/requests/utils.py

    from urllib.request import (
        getproxies,
        getproxies_environment,
        parse_http_list,
        proxy_bypass,
        proxy_bypass_environment,
    )

    for line in header_bytes.split(b"\r\n"):
        print(parse_http_list(line.decode("utf8", errors="surrogateescape")))

"""
import cgi
import werkzeug
"""
