def get_invite_content_template(organization_name: str, url: str) -> str:
    return (
        '<div>'
        '<h1>Здравствуйте!</h1>'
        '<div style="max-width: 536px; '
        'font-family: Arial, Helvetica, Tahoma, sans-serif; '
        'font-size: 16px; line-height: 20px; color:#262626">'
        f'Вас приглашают в организацию {organization_name}. '
        'Нажмите на кнопку ниже, чтобы начать работу.</div>'
        '<a style="display: inline-block; '
        'font-family: Arial, Helvetica, Tahoma, sans-serif; '
        'font-size: 16px; line-height: 20px; '
        'padding: 10px 20px; text-align: center; '
        'text-decoration: none; color: #ffffff; '
        'background-color: #5282ff; border-radius: 8px; '
        'outline: none; transition: 0.3s; border: 2px solid transparent;" '
        f'href="{url}"><span>Принять приглашение</span></a>'
    )
