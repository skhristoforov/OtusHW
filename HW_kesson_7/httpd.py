import sys
import socket
import logging
import re
from threading import Thread
from HW_kesson_7.reqresp import *


logging.basicConfig(
    format='[%(asctime)s]\t%(levelname)-8s\t%(message)s',
    level=logging.DEBUG
)


def _process_logger(before=None, after=None):
    def wrapper(f):
        def wrapped(*args, **kwargs):
            if before:
                logging.info(before)
            output = f(*args, **kwargs)
            if after:
                logging.info(after)
            return output
        return wrapped
    return wrapper


class PyServer:

    @_process_logger(before='Creating Python HTTP Server...')
    def __init__(self, host='127.0.0.1', port=8080, workers=50, socket_timeout=100.):
        logging.info('Created on {}:{}'.format(host, port))
        self.DOCUMENT_ROOT = '../../http-test-suite/httptest'
        self.terminator = '\r\n\r\n'
        self.workers = workers
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(workers)
        self.socket.settimeout(socket_timeout)
        self.__shutdown_request = False
        self.chunk_size = 2048

    @_process_logger(before='Waiting connections...')
    def launch(self):
        """Launching Python Server method"""
        try:
            while not self.__shutdown_request:
                c_socket, c_address = self.socket.accept()
                logging.info('Received connection from {}:{}'.format(c_address[0], c_address[1]))

                try:
                    worker = Thread(target=self._query_handler, args=(c_socket, ))
                    worker.start()
                except c_socket.error as se:
                    logging.critical('Socket exception occurred.')
                    logging.critical('{}'.format(se))
        except Exception as exc:
            logging.critical('Exception occurred. Shutting down.')
            logging.critical('{}'.format(exc))
            sys.exit()
        finally:
            self.socket.close()

    @_process_logger(after='Shutting down.')
    def stop(self):
        """Shutting down method"""
        self.__shutdown_request = True

    @_process_logger(before='Starting worker...', after='Worker stopped.')
    def _query_handler(self, client_socket):
        """Handling process of receiving and sending data"""
        request = self._receive_all(client_socket)

        path = self._parse_filepath(request=request)
        try:
            try:
                with open(self.DOCUMENT_ROOT + path, 'r') as f:
                    content = f.read()
            except UnicodeDecodeError:
                with open(self.DOCUMENT_ROOT + path, 'rb') as f:
                    content = f.read()
            f.close()
            content_type = (re.search('\.(\w+)$', path).group(0)[1:]).lower()

            if re.match('GET', request):
                response = BaseAnswer(200, content_type=content_type, content=content)
            elif re.match('HEAD', request):
                response = BaseAnswer(200, content_type=content_type, content=content, header_only=True)
            else:
                response = BaseAnswer(405)
        except FileNotFoundError:
            response = BaseAnswer(404)
        except Exception as e:
            response = BaseAnswer(500)

        # Sending response and closing socket
        self._send_all(client_socket, response)
        client_socket.close()

    def _receive_all(self, client_socket):
        """Receive data string method"""
        data = ''
        while True:
            data += client_socket.recv(self.chunk_size).decode('utf-8')
            if self.terminator in data:
                break
        return data[:-4]

    @staticmethod
    def _send_all(client_socket, message):
        """Send data string method"""
        client_socket.sendall(message.head())
        if not message.header_only:
            client_socket.sendall(message.body())

    @staticmethod
    def _parse_filepath(request):
        # Parsing request and creating response
        request_splitted = re.split('\s|\n', request)

        # Defining file path
        path = request_splitted[1]
        if path == '//' or path == '/':
            path = '/index.html'
        # Replacing spaces
        path = re.sub('%20', ' ', path)
        return path


if __name__ == '__main__':
    server = PyServer()
    server.launch()
    pass
