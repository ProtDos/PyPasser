from pypasser.exceptions import RecaptchaTokenNotFound, RecaptchaResponseNotFound
from pypasser.session import Session
from pypasser.structs import Proxy
from pypasser.utils import parse_url
from .constants import POST_DATA, BASE_URL, BASE_HEADERS
import re
import aiohttp
import asyncio
from typing import Dict, Union

class reCaptchaV3:
    """
    reCaptchaV3 bypass
    -----------------
    Bypass reCaptcha V3 only by sending HTTP requests.
    
    Attributes
    ----------
    anchor_url: str
        The anchor url.
        
    proxy [Optional]: Proxy or Dict,
        Proxy object from `pypasser.structs` or dict (for requests library).

    timeout [Optional]: int or float,
        the number of seconds to wait on a response before timing out.
    """
    def __new__(cls, *args, **kwargs) -> str:
        instance = super(reCaptchaV3, cls).__new__(cls)
        instance.__init__(*args,**kwargs)
        
        cls.session = Session(BASE_URL, BASE_HEADERS, instance.timeout, instance.proxy)
        
        data = parse_url(instance.anchor_url)
        
        # Gets recaptcha token.
        token = cls.get_recaptcha_token(data['endpoint'],
                                        data['params']
                                        )
        
        params = dict(pair.split('=') for pair in data['params'].split('&'))
         
        # Gets recaptcha response.
        post_data = POST_DATA.format(params["v"], token,
                                     params["k"], params["co"])
        
        recaptcha_response = cls.get_recaptcha_response(data['endpoint'],
                                                        f'k={params["k"]}',
                                                        post_data
                                                        )
        
        return recaptcha_response
        
    def __init__(self, anchor_url: str,
                proxy: Union[Proxy, Dict] = None,
                timeout: Union[int, float] = 20):
        
        self.anchor_url = anchor_url
        self.proxy = proxy
        self.timeout = timeout
                   
    def get_recaptcha_token(endpoint: str, params: str) -> str:
        """
        Sends GET request to `anchor URL` to get recaptcha token.
        
        """
        response = reCaptchaV3.session.send_request(
                                f"{endpoint}/anchor", params=params)
        
        results = re.findall(r'"recaptcha-token" value="(.*?)"', response.text)
        if not results:
            raise RecaptchaTokenNotFound()
        
        return results[0]
            

    def get_recaptcha_response(endpoint: str, params: str, data: str) -> str:
        """
        Sends POST request to `reload URL` to get recaptcha response.
        
        """
        response = reCaptchaV3.session.send_request(
                                f"{endpoint}/reload", data=data, params=params)
        
        results = re.findall(r'"rresp","(.*?)"', response.text)
        if not results:
            raise RecaptchaResponseNotFound()
        
        return results[0]


class AsyncReCaptchaV3:
    """
    Asynchronous reCaptchaV3 bypass using aiohttp.
    """

    def __init__(
            self,
            anchor_url: str,
            proxy: Union[Proxy, Dict] = None,
            timeout: Union[int, float] = 20,
    ):
        self.anchor_url = anchor_url
        self.proxy = proxy
        self.timeout = timeout
        self.prefix = "https://www.google.com/recaptcha/"

    async def solve(self) -> str:
        """
        Solves the reCaptcha v3 asynchronously.
        """
        data = parse_url(self.anchor_url)

        async with aiohttp.ClientSession(headers=BASE_HEADERS) as session:
            # Gets recaptcha token.
            token = await self.get_recaptcha_token(session, data["endpoint"], data["params"])

            params = dict(pair.split("=") for pair in data["params"].split("&"))

            # Gets recaptcha response.
            post_data = POST_DATA.format(params["v"], token, params["k"], params["co"])

            recaptcha_response = await self.get_recaptcha_response(session, data["endpoint"], f'k={params["k"]}',
                                                                   post_data)

        return recaptcha_response

    async def get_recaptcha_token(self, session: aiohttp.ClientSession, endpoint: str, params: str) -> str:
        """
        Sends GET request to `anchor URL` to get recaptcha token asynchronously.
        """
        async with session.get(f"{self.prefix}{endpoint}/anchor", params=params) as response:
            response_text = await response.text()

        results = re.findall(r'"recaptcha-token" value="(.*?)"', response_text)
        if not results:
            raise RecaptchaTokenNotFound()

        return results[0]

    async def get_recaptcha_response(self, session: aiohttp.ClientSession, endpoint: str, params: str,
                                     data: str) -> str:
        """
        Sends POST request to `reload URL` to get recaptcha response asynchronously.
        """
        async with session.post(f"{self.prefix}{endpoint}/reload", params=params, data=data) as response:
            response_text = await response.text()

        results = re.findall(r'"rresp","(.*?)"', response_text)
        if not results:
            raise RecaptchaResponseNotFound()

        return results[0]

