import socket
import logging
import time


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


class PyServerClient:

    class TimeoutWaiter:
        """Timeout waiter class. Calculates timeout as start ** pow.
        Then Increments pow"""
        def __init__(self, start=-1, pow=2.):
            self.pow = pow
            self.counter = start

        def __call__(self, *args, **kwargs):
            result = self.pow ** self.counter
            self.counter += 1
            return result

        def reset(self):
            self.counter = 0

        def get_current_value(self):
            return self.pow ** self.counter

    @_process_logger(before='Creating PyServerClient')
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.terminator = '\r\n\r\n'

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

    def send(self, raw):
        """Send data string method"""
        message = raw + self.terminator
        logging.info('Sending message "{}"'.format(raw))
        self.socket.sendall(message.encode('utf-8'))

    def receive(self):
        """Receive data string method"""
        data = ''
        while True:
            data += self.socket.recv(2048).decode('utf-8')
            if self.terminator in data:
                break
        return data

    def close_connection(self):
        self.socket.close()


if __name__ == '__main__':
    client = PyServerClient()

    output = []
    for i in range(5):
        client.connect('127.0.0.1', 8080)
        client.send('Hello {}'.format(i))
        output.append(client.receive())
        client.close_connection()
    for val in output:
        print(val)
