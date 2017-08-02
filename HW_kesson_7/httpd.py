import socket
import logging
from multiprocessing import Process


logging.basicConfig(
    format='%(levelname)-8s [%(asctime)s] %(message)s',
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
    def __init__(self, host='127.0.0.1', port=9000, workers=10):
        logging.info('\tCreated on {}:{}'.format(host, port))
        self.workers = workers
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen(workers)
        self.__shutdown_request = False

    @_process_logger(before='Waiting connections...')
    def launch(self):
        try:
            while not self.__shutdown_request:
                csocket, caddress = self.socket.accept()
                logging.info('Received connection from {}:{}'.format(caddress[0], caddress[1]))

                try:
                    worker = Process(target=self.query_handler, args=(csocket, ))
                    worker.start()
                except csocket.error as se:
                    logging.critical('Socket exception occurred.')
                    logging.critical('{}'.format(se))
        except Exception as exc:
            logging.critical('Exception occurred. Shutting down.')
            logging.critical('{}'.format(exc))
        finally:
            self.socket.close()

    @staticmethod
    @_process_logger(before='Starting worker...', after='Worker stopped.')
    def query_handler(client_socket):
        while True:
            data = client_socket.recv(2048)
            if not data:
                break
            # client_socket.sendall(data)

        # Processing

        client_socket.close()

    @_process_logger(after='Shutting down.')
    def shutdown(self):
        self.__shutdown_request = True


if __name__ == '__main__':
    server = PyServer()
    server.launch()
    pass
