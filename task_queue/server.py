import dbm
from threading import Timer
import socket
import shelve
from collections import deque
import logging
from uuid import uuid1


class Task:
    def __init__(self, length, data):
        self.length = length
        self.data = data
        self.id = uuid1().hex
        self.worker = None
        self.work = False

    def __repr__(self):
        return '(id: {}, work: {})'.format(self.id, self.work)

    def after_time_limit(self, queue_name):
        logging.info('---Ответ: задача с id {} в {} не выполнена'.format(self.id, queue_name))
        self.worker = None
        self.work = False


class Server:
    DEBUG = True
    OPEN_LOG = False

    def __init__(self, port=8080, time_limit=1):
        if Server.DEBUG and not Server.OPEN_LOG:
            self._debug()
            Server.OPEN_LOG = True
        logging.info('=' * 20)
        self.port = port
        self.time_limit = time_limit*60
        self._command = {
            'ADD': self.add_command,
            'GET': self.get_command,
            'ACK': self.ack_command,
            'IN': self.in_command,
        }
        self.queues = {}
        self.listen()

    @classmethod
    def _debug(cls):
        logging.basicConfig(
            handlers=[logging.FileHandler('server.log', 'a', 'utf-8')],
            level=logging.INFO,
            format='[%(asctime)s] %(message)s',
            datefmt='%I:%M:%S'
        )

    def write_current_state(self):
        data = {}
        with shelve.open("last_state", 'n') as db:
            for queue_name, tasks in self.queues.items():
                data[queue_name] = deque()
                for task in tasks:
                    if not task.work:
                        data[queue_name].append(task)
                    else:
                        # Что бы не сбросить текущий поток, создаем копию задачи
                        copy_task = Task(
                            length=task.length,
                            data=task.data
                        )
                        copy_task.id = task.id
                        copy_task.worker = None
                        copy_task.work = True
                        data[queue_name].append(copy_task)
            db['state'] = data

    def read_last_state(self):
        with shelve.open("last_state", 'r') as db:
            self.queues = db['state']
            for queue_name, tasks in self.queues.items():
                for task in tasks:
                    if task.work:
                        task.worker = Timer(self.time_limit, function=task.after_time_limit, args=(queue_name,))
                        task.worker.start()
                        logging.info('---Ответ: задача с id {} выдана из {}'.format(task.id, queue_name))

    def get_command(self, queue_name):
        logging.info('--Выполняется GET')
        queue = self.queues.get(queue_name)
        if queue:
            for task in queue:
                if not task.work:
                    task.work = True
                    task.worker = Timer(self.time_limit, function=task.after_time_limit, args=(queue_name,))
                    task.worker.start()

                    logging.info('---Состояние: ' + str(self.queues))
                    self.write_current_state()
                    logging.info('---Ответ: задача с id {} выдана из {}'.format(task.id, queue_name))
                    return task.id + ' ' + str(task.length) + ' ' + str(task.data)

        logging.info('---Ответ: нет задач для выдачи из {}'.format(queue_name))
        return 'None'

    def ack_command(self, queue_name, num):
        logging.info('--Выполняется ACK')
        queue = self.queues.get(queue_name)
        for task in queue:
            if task.id == num and task.worker:
                task.worker.cancel()
                queue.remove(task)
                del task

                logging.info('---Состояние: ' + str(self.queues))
                self.write_current_state()
                logging.info('---Ответ: задача с id {} в {} выполнена'.format(num, queue_name))
                return 'YES'

        logging.info('---Ответ: задача с id {} в {} не требует выполнения'.format(num, queue_name))
        return 'NO'

    def in_command(self, queue_name, num):
        logging.info('--Выполняется IN')
        for task in self.queues.get(queue_name):
            if task.id == num:
                logging.info('---Состояние: ' + str(self.queues))
                logging.info('---Ответ: задача с id {} в {} нашлась'.format(num, queue_name))
                return 'YES'
        logging.info('---Состояние: ' + str(self.queues))
        logging.info('---Ответ: задача с id {} в {} не нашлась'.format(num, queue_name))
        return 'NO'

    def add_command(self, queue_name, length, data):
        logging.info('--Выполняется ADD')
        queue = self.queues.get(queue_name)
        if not queue:
            self.queues[queue_name] = deque()
            queue = self.queues.get(queue_name)
        task = Task(length, data)
        queue.append(task)

        logging.info('---Состояние: ' + str(self.queues))
        self.write_current_state()
        logging.info('---Ответ: задача с Id {} добавлена в {}'.format(task.id, queue_name))
        return task.id

    def listen(self):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind(('127.0.0.1', self.port))
        connection.listen(10)

        logging.info('Сервер начал работу')
        try:
            self.read_last_state()
        except dbm.error:
            pass
        logging.info('---Состояние: ' + str(self.queues))

        while True:
            current_connection, address = connection.accept()

            logging.info('Сервер установил соединение ' + str(address))
            try:
                self.read_last_state()
            except dbm.error:
                pass
            logging.info('---Состояние: ' + str(self.queues))

            while True:
                data = current_connection.recv(2048)
                message = bytes.decode(data)

                if not message:

                    logging.info('Сервер закрыл соединение ' + str(address))
                    logging.info('---Состояние: ' + str(self.queues))
                    self.write_current_state()

                    for queue, tasks in self.queues.items():
                        for task in tasks:
                            if task.work and task.worker:
                                task.worker.cancel()
                                task.worker = None

                    current_connection.shutdown(1)
                    current_connection.close()
                    logging.info('='*20)

                    break

                else:
                    logging.info('-На сервер пришла команда: ' + message)
                    message = bytes.decode(data).split()
                    command = message[0]
                    args = message[1:]
                    func = self._command.get(command)
                    if func:
                        try:
                            result = func(*args)
                        except TypeError:
                            result = 'Not valid command'
                            logging.info('-Эта команда неверная')
                    else:
                        result = 'Not valid command'
                        logging.info('-Эта команда неверная')

                    current_connection.send(result.encode())


if __name__ == '__main__':
    Server()
