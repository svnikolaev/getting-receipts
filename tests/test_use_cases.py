import datetime
import logging
import random
import string

import src.domain.models as model
import src.domain.use_cases as use_case
from src.adapters.gateways import AbstractGateway
from src.adapters.repositories import AbstractRepository
from src.domain.interfaces import AbstractContext
from tests.data_receipts import data_tickets


class FakeSessionTokenRepository(AbstractRepository):
    class FakeSession:
        @staticmethod
        def commit():
            logging.debug('Fake commit')

        @staticmethod
        def refresh(arg):
            logging.debug('Fake refresh')

    def __init__(self, tokens_data: dict = {}, init_id: int | None = None):
        self.tokens_data = tokens_data
        if not init_id:
            self.init_id = random.randint(100, 9999)
        else:
            self.init_id = init_id
        self._current_id = self.init_id
        if self.tokens_data:
            logging.debug('FakeRepository initialized')
        else:
            logging.debug('FakeRepository initialized with empty data dict')
        logging.debug(f'initial id is {self._current_id}')
        self.session = self.FakeSession()
        print(f'initial id is {self._current_id}')

    def issue_next_id(self):
        issued_id = self._current_id
        self._current_id += 1
        return issued_id

    def add(self, Entity: model.SessionToken):
        Entity.id = self.issue_next_id()
        Entity.time_created = datetime.datetime.now()
        if not self.tokens_data.get(str(Entity.__class__.__name__)):
            self.tokens_data[str(Entity.__class__.__name__)] = {}
        self.tokens_data[str(Entity.__class__.__name__)][Entity.id] = Entity

    def get(self, EntityType: type, entity_id: int) -> object:
        return self.tokens_data[str(EntityType.__name__)][entity_id]

    def get_last(self,
                 EntityType=model.SessionToken) -> model.SessionToken | None:
        if self.tokens_data:
            last_id = list(self.tokens_data[EntityType.__name__].keys())[-1]
            return self.tokens_data[str(EntityType.__name__)].get(last_id)
        return None

    def get_all_data(self) -> dict:
        return self.tokens_data


class FakeReceiptGateway(AbstractGateway):
    def __init__(self, data: dict, response_list: list = []):
        self.data = data
        self.response_list = response_list

    @staticmethod
    def random_word(length):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(length))

    def get_response(self) -> dict[str, str]:
        r = {'refresh_token': self.random_word(36),
             'session_id': self.random_word(61), }
        sr = r.copy()
        sr['session_id_dt'] = datetime.datetime.now()
        self.response_list.append(sr)
        return r

    def request_sms_code(self, phone: str) -> bool:
        logging.debug('Fake request for sms code')
        return True

    def request_session_id_by_code(self, phone: str,
                                   SMS_code: str) -> dict[str, str]:
        logging.debug(f'The phone is "{phone}", the code is "{SMS_code}"')
        return self.get_response()

    def request_session_id_by_refresh_token(
        self, refresh_token: str
    ) -> dict[str, str] | None:
        if self.response_list and (
            self.response_list[-1].get('refresh_token') == refresh_token
        ):
            return self.get_response()
        return None

    def get_ticket_id(self, qr: str, session_id: str) -> str | None:
        ticket_id = self.data['qr'].get(qr)
        if ticket_id:
            return ticket_id
        return None

    def get_ticket_by_id(self, ticket_id: str, session_id: str) -> dict | None:
        ticket = self.data['ticket'].get(ticket_id)
        if ticket:
            return ticket
        return None


class FakeContext(AbstractContext):
    client: FakeReceiptGateway
    repo: FakeSessionTokenRepository


class TestClassReceipts:
    qr = 't=20210123T2022&s=1000.80&fn=9960440302630000&i=100000&fp=4280030000&n=1'  # noqa E510

    def test_get_receipt_success(self):
        fake_context = FakeContext(
            client=FakeReceiptGateway(data=data_tickets),
            repo=FakeSessionTokenRepository(tokens_data={})
        )
        new_token_by_sms = use_case.get_session_token_by_sms_code(
            phone='+70000000000', sms_code='0000', ctx=fake_context
        )
        logging.debug(f'{new_token_by_sms=}')
        receipt_by_qr = use_case.get_receipt(qr=self.qr, ctx=fake_context)
        assert receipt_by_qr == data_tickets['ticket']['00a37c000a0e00000a9ad4a0']  # noqa E510

    def test_get_receipt_fail(self):
        fake_context = FakeContext(
            client=FakeReceiptGateway(data=data_tickets),
            repo=FakeSessionTokenRepository(tokens_data={})
        )
        receipt_by_qr = use_case.get_receipt(qr=self.qr, ctx=fake_context)
        logging.debug(f'{receipt_by_qr=}')
        assert receipt_by_qr is None
