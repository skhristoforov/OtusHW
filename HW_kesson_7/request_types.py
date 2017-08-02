import urllib.request as request
import urllib.response as response
import urllib.parse as parse


class BaseAnswer:

    def __init__(self):
        self.responses = {
            200: ('OK', 'Request fulfilled, document follows'),
            404: ('Not Found', 'Nothing matches the given URI'),
            405: ('Method Not Allowed', 'Specified method is invalid for this server.')
        }


class GetAnswer(BaseAnswer):

    def __init__(self):
        super().__init__()
        pass

    def make(self, title='Success', body='body'):
        pass