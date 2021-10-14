import os


class Config:
    TOKEN = os.getenv('TOKEN')
    USER = {
        # TODO(redd4ford) user authentication
        'id': 'TG_ID',
        'is_schedule': False,
        'networks': {}
    }
    TIME_TO_PING = 10
