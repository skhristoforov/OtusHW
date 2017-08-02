import socket
import logging
from threading import Thread

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
    def __init__(self, host='127.0.0.1', port=8080, workers=10):
        logging.info('Created on {}:{}'.format(host, port))
        self.terminator = '\r\n\r\n'
        self.workers = workers
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.bind((host, port))
        except OSError:
            logging.warning('Socket is already in use. Reopening...')
            self.socket.close()
            self.socket.bind((host, port))
        self.socket.listen(workers)
        self.__shutdown_request = False

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
        finally:
            self.socket.close()

    @_process_logger(before='Starting worker...', after='Worker stopped.')
    def _query_handler(self, client_socket):
        """Handling process of receiving and sending data"""
        data = ''
        while True:
            data += client_socket.recv(2048).decode('utf-8')
            if self.terminator in data:
                break

        # Processing
        client_socket.sendall(data.encode('utf-8'))
        client_socket.close()

    @_process_logger(after='Shutting down.')
    def shutdown(self):
        """Shutting down method"""
        self.__shutdown_request = True


if __name__ == '__main__':
    server = PyServer()
    server.launch()
    pass
