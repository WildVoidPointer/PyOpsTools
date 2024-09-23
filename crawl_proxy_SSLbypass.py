from urllib.request import install_opener, BaseHandler, OpenerDirector
from urllib.request import build_opener, ProxyHandler, HTTPSHandler
from http.client import HTTPResponse
from urllib.error import URLError
import ssl


def get_proxy_handler(
        http: str | None = None, https: str | None = None ) -> ProxyHandler:
    
    _proxy: dict[str, str] = {}

    if isinstance(http, str):
        _proxy["http"] = http

    if isinstance(https, str):
        _proxy["https"] = https

    if not _proxy:
        return ProxyHandler()

    return ProxyHandler(_proxy)


def get_ssl_bypass_https_handle() -> HTTPSHandler:
    _context = ssl.create_default_context()
    _context.check_hostname = False
    _context.verify_mode = ssl.CERT_NONE
    return HTTPSHandler(context=_context)


def get_proxy_ssl_bypass_opener(
        proxy: ProxyHandler, *args: BaseHandler) -> OpenerDirector:
    return build_opener(proxy, *args)


def set_global_opener(opener: OpenerDirector) -> None:
    if isinstance(opener, OpenerDirector):
        install_opener(opener)


if __name__ == "__main__":
    http_proxy: str = "http://127.0.0.1:8080"
    https_proxy: str = "http://127.0.0.1:8080"

    proxy = get_proxy_handler(http_proxy, https_proxy)

    https_handle = get_ssl_bypass_https_handle()

    opener = get_proxy_ssl_bypass_opener(proxy, https_handle)

    visit_target_url = "https://www.baidu.com"

    try:
        res: HTTPResponse = opener.open(visit_target_url)
        html_document = res.read().decode("utf-8")
        print(html_document)
    except URLError as e:
        print(e.reason)

