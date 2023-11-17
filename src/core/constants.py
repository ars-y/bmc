import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

###############################################################################
# APPLICATION INFO
###############################################################################

TITLE_APP: str = 'BMC'

DESCRIPTION_APP: str = 'Business Management and Control System'

###############################################################################
# PASSWORD PATTERN
###############################################################################


class PasswordConst:

    PATTERN: str = r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[a-zA-Z])(?=.*[!-@_#$%^&*]).{8,30}$'
    MIN_LEN: int = 8
    MAX_LEN: int = 30
    ALLOWED_PUNCTUATIONS: str = '!-@_#$%^&*'


###############################################################################
# ERROR CODES
###############################################################################

class ErrorCode:

    INVALID_EMAIL: str = 'Invalid email'
    INVALID_PASSWORD: str = 'Invalid password'
    INCORRECT_PASSWORD: str = (
        f'Password must contain minimum {PasswordConst.MIN_LEN} characters, '
        'at least one uppercase letter, '
        'one lowercase letter, '
        'one number and one special character'
    )
    SAME_PASSWORD: str = (
        'The new password must be different from the old one'
    )


###############################################################################
# ETC
###############################################################################

INVITE_EXPIRE_SECONDS: int = 60*60*24*7

###############################################################################
# SUPERUSER DATA
###############################################################################

SUPERUSER_USERNAME: str = str(os.getenv('SUPERUSER_USERNAME', 'admin'))

SUPERUSER_PASSWORD: str = str(os.getenv('SUPERUSER_PASSWORD', 'Qwerty_123'))
