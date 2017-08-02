import socket
import logging
import time


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


class TimeoutWaiter:

    def __init__(self, start_value=0., velocity=2.):
        self.start = start_value
        self.velocity = velocity
        self.exec_counter = 0

    def __call__(self, *args, **kwargs):
        result = self.start + self.velocity ** self.exec_counter
        self.exec_counter += 1
        return result

    def reset(self):
        self.exec_counter = 0

    def get_current_value(self):
        return self.start + self.velocity ** self.exec_counter


class PyServerClient:

    @_process_logger(before='Creating PyServerClient')
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port, attempts=5, timeout_fun=TimeoutWaiter()):
        logging.info('Connecting to {}:{}'.format(host, port))
        try:
            self.socket.connect((host, port))
        except OSError:
            logging.warning('Can not connect. Trying to reconnect...')
            current_attempt = 0
            while current_attempt < attempts:
                try:
                    logging.warning('\tAttempt #{}: {} seconds'.format(
                        current_attempt + 1,
                        timeout_fun.get_current_value()
                    ))
                    self.reconnect(host, port)
                    break
                except ConnectionRefusedError:
                    current_attempt += 1
                    time.sleep(timeout_fun())
            else:
                logging.critical('Can not connect to server. Shutting down.')
                raise Exception('Can not connect to server. Shutting down.')

    @_process_logger(before='Reconnection...')
    def reconnect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))

    def send(self, message):
        logging.info('Sending message "{}"'.format(message))
        self.socket.sendall(message.encode('utf-8'))

    def close_connection(self):
        self.socket.close()


if __name__ == '__main__':
    client = PyServerClient()

    for i in range(5):
        client.connect('127.0.0.1', 9000)
        client.send('Hello {}'.format(i))
        print(client.socket.recv(2048).decode('utf-8'))
        client.close_connection()
