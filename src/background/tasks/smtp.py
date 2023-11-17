from email.message import EmailMessage

from src.core.settings.base import settings
from src.templates.invite import get_invite_content_template


def get_email_invite_template(data: dict) -> EmailMessage:
    org_name: str = data.get('organization').get('name')
    code: str = data.get('code')
    email_from: str = data.get('invited_by').get('email')
    email_to: str = data.get('invitee').get('email')

    url: str = f'{settings.ADDRESS_URL}auth/join/invitation?code={code}'
    content: str = get_invite_content_template(org_name, url)

    email_msg = EmailMessage()
    email_msg['Subject'] = 'Вы приглашены в организацию'
    email_msg['From'] = email_from
    email_msg['To'] = email_to

    email_msg.set_content(content, subtype='html')
    return email_msg
