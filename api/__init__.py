import datetime
from cloudscraper import CloudScraper
from typing import Dict, Any, Union

from .cookies import load_cookies, save_cookies
from .states import load_states, save_states, _create_dirs
from .models import ClientOperations

API_URL = "https://finance.ozon.ru/api/v2/"

_create_dirs()

class OzonPAY(CloudScraper):
    def __init__(
        self,
        pincode: str,
        cookie: str = None
    ):
        super().__init__()
        self.cookies_dict = None
        self.cookies_string = None
        self.__pin = pincode
        self.states = load_states()
        self._prepare_cookies(cookie or load_cookies())

    def _prepare_cookies(self, cookie: Union[str, dict]):
        if isinstance(cookie, str):
            self.cookie_string = cookie
            self.cookie_dict = {k: v for k, v in [c.split("=") for c in self.cookie_string.split("; ")]}
        elif isinstance(cookie, dict):
            self.cookie_dict = cookie
            self.cookie_string = "; ".join([f"{k}={v}" for k, v in self.cookie_dict.items()])

    def get_invoice(
        self,
        sum: int
    ) -> Dict[str, Any]:
        """
        Получает инвойс из состояния.
        """
        return self.states.get(sum)

    def __call__(
        self,
        method: str,
        json: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        _method: str = "post",
        **kwargs
    ) -> Dict[str, Any]:
        return self._request(method, json, params, _method, **kwargs)

    def __delitem__(
        self,
        key: float
    ) -> None:
        del self.states[key]
        save_states(self.states)

    def __setitem__(
        self,
        item: float,
        value: Dict[str, Any]
    ) -> None:
        self.states[float(item)] = value
        save_states(self.states)

    def __getitem__(
            self,
            item: float
    ) -> Dict[str, Any]:
        return self.states.get(item)

    @staticmethod
    def _now() -> datetime.datetime:
        return datetime.datetime.now(tz=datetime.timezone.utc)

    @staticmethod
    def _str_time(
        _time: datetime.datetime
    ) -> str:
        return _time.strftime("%d.%m.%Y %H:%M:%S")

    def _request(
        self,
        method: str,
        json: Dict[str, Any] = None,
        params: Dict[str, Any] = None,
        _method: str = "post",
        **kwargs
    ) -> Dict[str, Any]:
        response = getattr(self, _method)(
            API_URL + method, json=json, params=params, headers=self._pre_headers(), cookies=self.cookies_dict,
            **kwargs
        )

        self.cookies_dict.update(response.cookies)
        save_cookies(self.cookies_dict)

        if response.status_code == 401:
            self._login()
            return self._request(method, json, params, _method)
        if response.status_code == 200:
            return response.json()
        return response

    @staticmethod
    def _cookies_to_json(
        string: str
    ) -> Dict[str, str]:
        return {cookie.split("=")[0].strip(): cookie.split("=")[1].strip() for cookie in string.split(";") if "=" in cookie}

    @staticmethod
    def _base_headers() -> Dict[str, str]:
        return {
            "accept": "application/json",
            "accept-language": "ru-RU,ru;q=0.7",
            "ob-client-version": "4e088df2",
            "origin": "https://finance.ozon.ru",
        }

    def _pre_headers(
        self
    ) -> Dict[str, str]:
        headers = self._base_headers()
        headers['cookie'] = self.cookies_string
        return headers

    def _login(
        self
    ) -> bool:
        """
        Повторно авторизируется. Используя пин-код
        """
        result = tuple(self("auth_login", {"pincode": self.__pin}).values())
        ok = result[0]
        if ok:
            self.__signToken = result[-1]
        return ok

    def get_credits(
        self,
        effect: str = "EFFECT_CREDIT"
    ) -> ClientOperations:
        """
        Получает входящие платежи.
        """
        return ClientOperations.de_json(self("clientOperations",
                                             {"filter": {"categories": [], "effect": effect},
                                              "cursors": {"next": None, "prev": None}, "perPage": 100}
                                             ))

    def auth_check(
        self
    ) -> Dict[str, Any]:
        return self("auth_check")

    def check_pay_by_sum(
        self,
        sum: int,
        _del_is_payed: bool = True
    ) -> bool | ClientOperations:
        """
        Проверяет оплату на заказ.
        """
        items = self.get_credits().items
        inv = self.get_invoice(sum)
        if not inv:
            return False
        for item in items:
            if (item.accountAmount / 100 == sum and
                    self._str_time(item.time.replace(tzinfo=datetime.timezone.utc)) > inv['created_at']):
                if _del_is_payed:
                    del self[sum]
                return item
        return False

    def create_invoice(
        self,
        sum: int,
        step: int = 0.01,
        payload: Dict[str, Any] = {}
    ) -> int:
        """
        Генерирует инвойс, если сумма уже есть в состояниях, то повышает {sum} на {step} пока сумма не будет свободна.
        """
        while self.get_invoice(sum):
            sum += step
            sum = round(sum, 2)
        data = {"created_at": self._str_time(self._now()), "data": payload}
        self[sum] = data
        return sum
