from abc import ABC, abstractmethod

import requests


class AbstractGateway(ABC):
    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    def request_sms_code(self, phone: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def request_session_id_by_code(
        self, phone: str, SMS_code: str
    ) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    def request_session_id_by_refresh_token(
        self, refresh_token: str
    ) -> dict[str, str]:
        raise NotImplementedError

    @abstractmethod
    def get_ticket_id(self, qr: str, session_id: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_ticket_by_id(self, ticket_id: str, session_id: str) -> dict:
        raise NotImplementedError


class ReceiptBase(AbstractGateway):
    def __init__(self, host: str, headers: dict, client_secret: str,
                 os: str = 'Android', timeout: int = 10):
        self.host = host
        self.headers = headers
        self.client_secret = client_secret
        self.os = os
        self.tt = timeout

    @staticmethod
    def check_response(r: requests.Response):
        if not r.ok:
            raise requests.RequestException(
                f'Bad response, Status Code: {r.status_code}, {r.reason}'
            )

    def request_sms_code(self, phone: str) -> bool:
        """Request SMS code to the specified phone number

        Args:
            phone (str): phone in +70000000000 format

        Returns:
            bool: True if response status_code is less than 400, False if not.
        """
        url = f'https://{self.host}/v2/auth/phone/request'
        headers = self.headers
        payload = {
            'phone': phone,
            'client_secret': self.client_secret,
        }
        r = requests.post(url, json=payload, headers=headers, timeout=self.tt)
        return r.ok

    def request_session_id_by_code(
        self, phone: str, SMS_code: str
    ) -> dict[str, str]:
        """Request session_id using phone and SMS code

        Args:
            phone (str): phone in +70000000000 format
            SMS_code (str): code in 0000 format

        Returns:
            dict[str, str]: session_id, refresh_token
        """
        url = f'https://{self.host}/v2/auth/phone/verify'
        headers = self.headers
        payload = {
            'phone': phone,
            'client_secret': self.client_secret,
            'code': SMS_code,
            "os": self.os
        }
        r = requests.post(url, json=payload, headers=headers, timeout=self.tt)
        self.check_response(r)
        session_id = r.json()['sessionId']
        refresh_token = r.json()['refresh_token']
        return {
            'session_id': session_id,
            'refresh_token': refresh_token
        }

    def request_session_id_by_refresh_token(
        self, refresh_token: str
    ) -> dict[str, str]:
        """Request session_id using last refresh token

        Args:
            refresh_token (str | None, optional): refresh token. Defaults
                    to None. Example "c68b4444-b1c7-4441-a446-cf403a134b74"

        Returns:
            dict[str, str]: dict[str, str]: session_id, refresh_token
        """
        url = f'https://{self.host}/v2/mobile/users/refresh'
        headers = self.headers
        payload = {
            'refresh_token': refresh_token,
            'client_secret': self.client_secret
        }
        r = requests.post(url, json=payload, headers=headers, timeout=self.tt)
        self.check_response(r)
        session_id = r.json()['sessionId']
        refresh_token = r.json()['refresh_token']
        return {
            'session_id': session_id,
            'refresh_token': refresh_token
        }

    def get_ticket_id(self, qr: str, session_id: str) -> str:
        """Get ticket id by qr code

        Args:
            qr (str): text from qr code.
                      Example "t=20221223T2022&s=1008.80&fn=9960440302630648&i=167649&fp=4280030804&n=1"
            session_id (str): Session id. Example "5db7981828ded41d0257826a:f008fd91-98ab-4ecc-92e8-c8f6773192ba"

        Returns:
            str: Ticket id. Example "63d37c643d0e75074b9ad4a6"
        """  # noqa E501
        url = f'https://{self.host}/v2/ticket'
        headers = self.headers
        headers.update({'sessionId': session_id})
        payload = {
            'qr': qr
        }
        r = requests.post(url, json=payload, headers=headers, timeout=self.tt)
        self.check_response(r)
        ticket_id = r.json()["id"]
        return ticket_id

    def get_ticket_by_id(self, ticket_id: str, session_id: str) -> dict:
        """Get ticket body by ticket id

        Args:
            ticket_id (str): Ticket id. Example "63d37c643d0e75074b9ad4a6"
            session_id (str): Session id. Example "5db7981828ded41d0257826a:f008fd91-98ab-4ecc-92e8-c8f6773192ba"

        Returns:
            dict: ticket body in JSON format
        """  # noqa E501
        url = f'https://{self.host}/v2/tickets/{ticket_id}'
        headers = self.headers
        headers.update({
            'sessionId': session_id,
            'Content-Type': 'application/json'
        })
        r = requests.get(url, headers=headers, timeout=self.tt)
        self.check_response(r)
        ticket = r.json()
        return ticket
