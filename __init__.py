import time
from http.cookies import SimpleCookie
from typing import Union

import js2py
import websocket

from logging_config import *
from lolzapi_formatter import *


class Params:
    LZT_URL = "https://zelenka.guru/"
    LZT_WEBSOCKET_URL = "wss://im.zelenka.guru/ws/{}?_={}"
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"


class Client:
    #  takes cookie string like "foo=bar; baz=val;"
    def __init__(self, cookie_string: str) -> None:
        if not cookie_string.endswith(";"):
            cookie_string += ";"

        cookie = SimpleCookie()
        cookie.load(cookie_string)

        self._xf_user = cookie.get("xf_user")
        self._xf_session = cookie.get("xf_session")
        self._xf_tfa_trust = cookie.get("xf_tfa_trust")
        self._sfwefwe = cookie.get("sfwefwe")  # will bypass it if its None

        self._websocket_connection = None
        self.xf_token = None
        self._cookie = cookie_string

        self.s = requests.session()
        self.s.headers["User-Agent"] = Params.USER_AGENT
        self.s.headers["Cookie"] = self._cookie

        response = self.send_request("GET", Params.LZT_URL)
        if "Im.username = '" not in response.text:
            print(response.status_code)
            raise ValueError("Invalid cookie")

        self.user_name = re.findall(r'Im.username = \'(.*?)\'', response.text, re.DOTALL)[0]
        self.user_id = self.xf_token.split(',')[0]

    # returns your user
    def get_me(self, return_response: bool = False):
        return self.get_user(self.user_id, return_response)

    # gets user by id / custom user link
    def get_user(self, user_id: Union[int, str], return_response: bool = False):
        if user_id.isdigit():
            url = f"{Params.LZT_URL}members/{user_id}/"
        else:
            url = f"{Params.LZT_URL}{user_id}/"

        response = self.send_request("GET", url)
        if return_response:
            return response
        return Response.get_user_response(response)

    # gets threads list of any category
    def get_thread(self, thread_id: Union[int, str]):
        # todo доделать прсмотр коментариев под сообщнеиями https://zelenka.guru/posts/35561336/comments?before=1671066888588&translateTo=(0+%3F%3F+0)&_xfRequestUri=%2Fthreads%2F4698784%2F&_xfNoRedirect=1&_xfToken=157562%2C1671070649%2C0dce965b1a0a7f0d5fc49d42c7bf814b2e9f85e4&_xfResponseType=json
        response = self.send_request("GET", f"{Params.LZT_URL}threads/{thread_id}/")
        return Response.get_thread_response(response)

    # gets threads list of any category
    def get_threads(self, category: Union[int, str]) -> dict:
        data = {
            "from_sidebar": True,
            "_xfRequestUri": "/",
            "_xfNoRedirect": 1,
            "_xfToken": self.xf_token,
            "_xfResponseType": "json"
        }

        response = self.send_request("POST", f"{Params.LZT_URL}forums/{category}/", data=data)
        return Response.get_threads_response(response)

    # get user's shared ips
    def get_shared_ips(self, user_id: Union[int, str], return_user_info: bool = False) -> Union[
        tuple[Response, Response], Response]:
        user = self.get_user(user_id=user_id, return_response=True)
        user_url = user.url.replace(Params.LZT_URL, "")
        response = self.send_request("GET",
                                     f"https://zelenka.guru/sociophob/shared-ips?&_xfRequestUri=/{user_url}&_xfNoRedirect=1&_xfToken={self.xf_token}&_xfResponseType=json")
        if return_user_info:
            return response, user
        return Response.get_shared_ips(response)

    def likes_inline(self, post_id: Union[int, str]) -> requests.models.Response:
        data = {
            "_xfRequestUri": f"/threads/4700304/",
            "_xfNoRedirect": 1,
            "_xfToken": self.xf_token,
            "_xfResponseType": "json"
        }
        response = self.send_request(method="GET", url=f"{Params.LZT_URL}posts/{post_id}/likes-inline", data=data)
        return Response.likes_inline(response)

    def like(self, post_id: Union[int, str], send_likes_inline: bool = True) -> requests.models.Response:
        data = {
            "_xfRequestUri": f"/threads/4700304/",
            "_xfNoRedirect": 1,
            "_xfToken": self.xf_token,
            "_xfResponseType": "json"
        }
        if send_likes_inline:
            self.likes_inline(post_id=post_id)
        response = self.send_request(method="GET", url=f"{Params.LZT_URL}posts/{post_id}/like", data=data)

        return Response.like(response)

    def get_payments(self):
        response = self.send_request("GET", f"https://zelenka.guru/market/user/{self.user_id}/payments")
        return response

    # todo delete this method
    def participate(self, contest_id: Union[int, str]):
        response = self.get_thread(thread_id=contest_id)
        requests_time = response.text.split('name="request_time" value="')[1].split('"')[0]
        data = {
            "request_time": requests_time,
            "_xfToken": self.xf_token,
            "_xfRequestUri": f"/threads/{contest_id}/",
            "_xfNoRedirect": 1,
            "_xfToken": self.xf_token,
            "_xfResponseType": "json"
        }
        response = self.send_request("POST", f"https://zelenka.guru/threads/{contest_id}/participate", data=data)
        return Response.participate(response)

    # follow the user by user id / custom link
    def follow(self, user_id: Union[int, str]):
        resp = self.send_request("GET",
                                 f"https://zelenka.guru/{user_id}/follow?_xfToken={self.xf_token}&_xfRequestUri=/{user_id}/&_xfNoRedirect=1&_xfToken={self.xf_token}&_xfResponseType=json")
        a = resp.json()
        data = {
            "_xfToken": self.xf_token,
            "_xfConfirm": 1
        }
        response = self.send_request("POST", f"https://zelenka.guru/{user_id}/follow", data=data)
        return Response.follow(response)

    # unfollow the user by user id / custom link
    def unfollow(self, user_id: Union[int, str]):
        resp = self.send_request("GET",
                                 f"https://zelenka.guru/gitl{user_id}er/unfollow?_xfToken={self.xf_token}&_xfRequestUri=/{user_id}/&_xfNoRedirect=1&_xfToken={self.xf_token}&_xfResponseType=json")
        a = resp.json()
        data = {
            "_xfToken": self.xf_token,
            "_xfConfirm": 1
        }
        response = self.send_request("POST", f"https://zelenka.guru/{user_id}/follow", data=data)
        return Response.unfollow(response)

    def send_request(self, method: str, url: str, data: dict = None,
                     retry_on_fail: bool = True) -> requests.models.Response:
        response = self.s.request(method=method, url=url, data=data)
        if response.status_code == 429:
            time.sleep(5)
            return self.send_request(method, url, data, retry_on_fail)

        self._webcocket_manager(response)

        logger.debug(f"Sent {method} request to {url} {response.status_code} | response length - {len(response.text)}")
        self._get_xf_token(response)

        if retry_on_fail:
            redirect_url = self._bypass_sfwefwe(response)  # get redirect url and bypass sfwefwe
            if redirect_url:
                return self.send_request(method, redirect_url, data, retry_on_fail)

        return response

    def _get_xf_token(self, response: requests.models.Response) -> None:
        if 'name="_xfToken" value="' in response.text:
            self.xf_token = response.text.split('name="_xfToken" value="')[1].split('"')[0]
        elif 'name=\\"_xfToken\\" value=\\"' in response.text:
            self.xf_token = response.text.split('name=\\"_xfToken\\" value=\\"')[1].split('\\"')[0]
        else:
            return

        logger.debug(f"New xf_token: {self.xf_token}")

    # not really good solution but it works stable
    def _bypass_sfwefwe(self, response: requests.models.Response) -> Union[None, str]:
        if not response.text.startswith("<"):  # return if it is json but not html
            return

        soup = BeautifulSoup(response.text, "html.parser")

        all_js = soup.find_all("script")

        if len(all_js) < 4:  # bypassing sfwefwe
            if not self._sfwefwe:
                js_code = self.s.get(f"{Params.LZT_URL}{all_js[0]['src']}").text + "\n\n" + all_js[-1].text

                js_code = js_code.replace("document.cookie=", "res=").replace(" max-age=86400; path=/", "")
                js_code = js_code.replace(f'window.location.href', "var window_location_href")
                js_code += "function complete() {return (res)} complete();"

                sfwefwe = js2py.eval_js(js_code)

                self.s.headers["Cookie"] += sfwefwe
                self._cookie += sfwefwe
                self._sfwefwe = sfwefwe

                logger.warning(f"Bypassed sfwefwe, the code is: {self._sfwefwe}")

            p = re.compile(r'window.location.href=\"(.*?)\"', re.DOTALL)
            redirect_url = p.findall(all_js[-1].text)[0]
            logger.debug(f"Redirect url - {redirect_url}")

            return redirect_url

    def _webcocket_manager(self, response: requests.models.Response):
        if "Im.visitorChannelId" not in response.text:
            return

        p = re.compile(r'Im.visitorChannelId = \'(.*?)\'', re.DOTALL)
        visitor_channel_id = p.findall(response.text)[0]

        if self._websocket_connection:
            self._websocket_connection.close()
            # todo connect to a new weboscket that appears only if thread is not closed
            pass

        url = Params.LZT_WEBSOCKET_URL.format(visitor_channel_id, str(time.time()).split(".")[0])
        self._websocket_connection = websocket.create_connection(url)
        logger.debug(f"Connected to WebSocket: {url}")
