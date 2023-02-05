from datetime import datetime, timedelta

import src.domain.interfaces as itf
import src.domain.models as model


def get_receipt(qr: str, ctx: itf.ReceiptContext) -> dict | None:
    receipt_id = get_receipt_id_by_qr(qr=qr, ctx=ctx)
    if receipt_id:
        receipt = get_receipt_by_id(receipt_id=receipt_id, ctx=ctx)
        if receipt:
            return receipt
    return None


def get_receipt_by_id(receipt_id: str, ctx: itf.ReceiptContext) -> dict | None:
    session_id = get_session_id(ctx=ctx)
    if session_id:
        ticket = ctx.client.get_ticket_by_id(ticket_id=receipt_id,
                                             session_id=session_id)
    if ticket:
        return ticket
    return None


def get_receipt_id_by_qr(qr: str, ctx: itf.ReceiptContext) -> str | None:
    session_id = get_session_id(ctx=ctx)
    if session_id:
        ticket_id = ctx.client.get_ticket_id(qr=qr, session_id=session_id)
        if ticket_id:
            return ticket_id
    return None


def get_session_id(ctx: itf.ReceiptContext,
                   session_id_lifetime_mins: int = 14,
                   dt_now: datetime = datetime.now()) -> str | None:
    token = ctx.repo.get_last(EntityType=model.SessionToken)
    session_id_lifetime = timedelta(minutes=session_id_lifetime_mins)
    if token and token.time_created and (
        dt_now - token.time_created < session_id_lifetime
    ):
        return token.session_id
    elif token and token.refresh_token:
        new_token = get_session_token_by_last_refresh_token(ctx=ctx)
        if new_token:
            return new_token.session_id
    return None


def get_session_token_by_last_refresh_token(
    ctx: itf.ReceiptContext
) -> model.SessionToken | None:
    session_token = ctx.repo.get_last(EntityType=model.SessionToken)
    if not session_token:
        return None
    vals = ctx.client.request_session_id_by_refresh_token(
        refresh_token=session_token.refresh_token
    )
    new_session_token = model.SessionToken(session_id=vals['session_id'],
                                           refresh_token=vals['refresh_token'])
    ctx.repo.add(new_session_token)
    ctx.repo.session.commit()
    ctx.repo.session.refresh(new_session_token)
    return new_session_token


def get_session_token_by_sms_code(phone: str, sms_code: str,
                                  ctx: itf.ReceiptContext) -> object:
    vals = ctx.client.request_session_id_by_code(phone=phone,
                                                 SMS_code=sms_code)
    new_token = model.SessionToken(session_id=vals['session_id'],
                                   refresh_token=vals['refresh_token'])
    new_token.obtained_using_code = True
    ctx.repo.add(new_token)
    ctx.repo.session.commit()
    ctx.repo.session.refresh(new_token)
    return new_token


def get_new_sms_code(phone: str, ctx: itf.ReceiptContext) -> None:
    ctx.client.request_sms_code(phone=phone)
