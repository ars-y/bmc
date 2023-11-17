from src.exceptions.bases import BadRequest


class InvalidData(BadRequest):

    DETAIL = 'Invalid data'
