from datetime import datetime


# Answers
class BaseAnswer:
    def __init__(self, status_code=200, content_type=None, content=None, header_only=False):
        self._date_format = '%a, %d %b %Y %H:%M:%S GMT'
        self._terminator = '\r\n\r\n'
        self.statuses = {
            200: 'HTTP/1.1 200 OK',
            404: 'HTTP/1.1 404 Not Found',
            405: 'HTTP/1.1 405 Method Not Allowed',
            500: 'HTTP/1.1 500 Internal Server Error'
        }
        self.content_types = {
            'txt': 'text',
            'html': 'text/html',
            'css': 'text/css',
            'js': 'text/javascript"',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'gif': 'image/gif',
            'swf': 'application/x-shockwave-flash'
        }

        self.status = status_code
        self.server = 'PyServer'
        self.content_type = content_type
        self.content = content
        self.header_only = header_only

        self.header = ''
        self.update()

    def update(self):
        self.header = ''
        if self.status:
            self.header += self.statuses[self.status]
        else:
            raise Exception('Define status line')

        self.header += '\nDate : {}'.format(datetime.utcnow().strftime(self._date_format))
        self.header += '\nServer : {}'.format(self.server)

        if self.content:
            if not self.content_type:
                raise Exception('Define content-type and content-length')
            self.header += '\nContent-type : {}'.format(self.content_types[self.content_type])
            self.header += '\nContent-length : {}'.format(len(self.content))

        self.header += self._terminator

    def head(self):
        return self.header.encode('utf-8')

    def body(self):
        if self.content:
            if type(self.content) == str:
                return self.content.encode('utf-8')
            elif type(self.content) == bytes:
                return self.content
            else:
                raise Exception('Bad content type')
        else:
            return b''


# Requests
class BaseRequest:
    def __init__(self):
        self.request = ''

    def __str__(self):
        return self.request


class GetRequest(BaseRequest):
    def __init__(self, host=None, body='/', headers={}):
        super().__init__()

        headers_str = ''
        for header in headers.keys():
            headers_str += '{}: {}\n'.format(header, headers[header])
        self.request = 'GET {} HTTP/1.1\nHost: {}\n{}Cache-Control: no-cache'.format(body, host, headers_str)


class HeadRequest(BaseRequest):
    def __init__(self, host=None, body='/', headers={}):
        super().__init__()

        headers_str = ''
        for header in headers.keys():
            headers_str += '{}: {}\n'.format(header, headers[header])
        self.request = 'HEAD {} HTTP/1.1\nHost: {}\n{}Cache-Control: no-cache'.format(body, host, headers_str)
