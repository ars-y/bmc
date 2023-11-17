import smtplib

from celery import Celery

from src.background.tasks.smtp import get_email_invite_template
from src.core.settings.base import settings


celery = Celery('tasks', broker=str(settings.REDIS_URL))


@celery.task
def send_email_org_invite(data: dict) -> None:
    email_msg = get_email_invite_template(data)
    with smtplib.SMTP_SSL(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.send_message(email_msg)
