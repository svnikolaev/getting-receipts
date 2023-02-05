import logging

from fastapi import FastAPI

import src.db as db
import src.domain.use_cases as use_case
from src.adapters.gateways import ReceiptBase as Client
from src.adapters.repositories import SessionTokensRepository as Repository
from src.domain.interfaces import ReceiptContext
from src.utils import get_settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(module)s:%(funcName)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
app = FastAPI()
logging.info('App started')

S = get_settings()
db.start_mappers()
db.mapper_registry.metadata.create_all(db.engine)


def get_context() -> ReceiptContext:
    ctx = ReceiptContext(
        client=Client(
            host=S.HOST,
            headers=S.get_headers(),
            client_secret=S.CLIENT_SECRET,
            os=S.OS,
        ),
        repo=Repository(session=db.Session()),
    )
    return ctx


@app.get("/")
async def root():
    return {"message": "Сервис: Просмотр чеков"}


@app.post("/get_sms_code")
async def get_sms_code(phone: str):
    """Request SMS code to the specified phone number

    Args:
        phone (str): phone in +70000000000 format
    """
    ctx = get_context()
    use_case.get_new_sms_code(phone=phone, ctx=ctx)


@app.post("/get_session_by_sms_code")
async def get_session_by_sms_code(phone: str, code: str):
    """Request session_id using phone and SMS code

    Args:
        phone (str): phone in +70000000000 format
        SMS_code (str): code in 0000 format
    """
    ctx = get_context()
    new_token = use_case.get_session_token_by_sms_code(
        phone=phone, sms_code=code, ctx=ctx
    )
    return new_token


@app.post("/get_receipt")
def get_receipt(qr: str):
    """Get receipt body by qr

    Args:
        qr (str): Example: "t=20210123T2022&s=1000.80&fn=9960440302630000&i=100000&fp=4280030000&n=1"
    """  # noqa #501
    ctx = get_context()
    receipt = use_case.get_receipt(qr=qr, ctx=ctx)
    return receipt
