import dbm
from threading import Thread
import socket
import shelve
from collections import deque
from time import sleep
import logging


class Task:
    def __init__(self, length, data, queue):
        self.length = length
        self.data = data
        self.id = self.generate_id(queue)
        self.worker = None
        self.work = False

    def __repr__(self):
        return '(id: {}, work: {})'.format(self.id, self.work)

    def working(self, limit, queue_name):
        sleep(limit)
        self.worker.is_alive()
        logging.info('---Ответ: задача с id {} в {} не выполнена'.format(self.id, queue_name))
        self.worker = None
        self.work = False

    @staticmethod
    def generate_id(queue):
        return str(len(queue))


class Server:
    DEBUG = True
    OPEN_LOG = False

    def __init__(self, port=8080, timelimit=5):
        if Server.DEBUG and not Server.OPEN_LOG:
            self._debug()
            Server.OPEN_LOG = True
        logging.info('=' * 20)
        self.port = port
        self.time_limit = timelimit
        self.command = {
            'ADD': self.add_task,
            'GET': self.get_task,
            'ACK': self.confirm_ready,
            'IN': self.check,
        }
        self.queues = {}
        self.listen()

    @classmethod
    def _debug(cls):
        logging.basicConfig(
            handlers=[logging.FileHandler('server.log', 'w', 'utf-8')],
            level=logging.INFO,
            format='[%(asctime)s] %(message)s',
            datefmt='%I:%M:%S'
        )

    def write_changed_state(self):
        data = {}
        with shelve.open("last_state.txt", 'n') as db:
            for queue, tasks in self.queues.items():
                data[queue] = deque()
                for task in tasks:
                    if not task.work:
                        data[queue].append(task)
                    else:
                        copy_task = Task(
                            length=task.length,
                            data=task.data,
                            queue=[]
                        )
                        copy_task.id = task.id
                        copy_task.worker = None
                        copy_task.work = True
                        data[queue].append(copy_task)
            db['state'] = data

    def read_last_state(self):
        with shelve.open("last_state.txt", 'r') as db:
            for queue, tasks in db['state'].items():
                for task in tasks:
                    if task.work:
                        task.worker = Thread(target=task.working, args=(self.time_limit, queue))
                        task.worker.start()
                        logging.info('---Ответ: задача с id {} выдана из {}'.format(task.id, queue))
            self.queues = db['state']

    def get_task(self, queue_name):
        logging.info('--Выполняется GET')
        queue = self.queues.get(queue_name)
        if queue:
            for task in queue:
                if not len(queue):
                    return None
                if not task.work:
                    task.worker = Thread(target=task.working, args=(self.time_limit, queue_name))
                    task.worker.start()
                    task.work = True
                    logging.info('---Состояние: ' + str(self.queues))
                    self.write_changed_state()
                    logging.info('---Ответ: задача с id {} выдана из {}'.format(task.id, queue_name))
                    return task.id + ' ' + str(task.length) + ' ' + str(task.data)
        logging.info('---Состояние: ' + str(self.queues))
        self.write_changed_state()
        logging.info('---Ответ: нет задач для выдачи из {}'.format(queue_name))
        return None

    def confirm_ready(self, queue_name, ident):
        logging.info('--Выполняется ACK')
        queue = self.queues.get(queue_name)
        for task in queue:
            if task.id == ident and task.worker:
                task.worker.is_alive()
                queue.remove(task)
                del task.worker
                del task
                logging.info('---Состояние: ' + str(self.queues))
                self.write_changed_state()
                logging.info('---Ответ: задача с id {} в {} выполнена'.format(ident, queue_name))
                return 'ok'

    def check(self, queue_name, ident):
        logging.info('--Выполняется IN')
        for task in self.queues.get(queue_name):
            if task.id == ident:
                logging.info('---Состояние: ' + str(self.queues))
                logging.info('---Ответ: задача с id {} в {} нашлась'.format(ident, queue_name))
                return 'YES'
        logging.info('---Состояние: ' + str(self.queues))
        logging.info('---Ответ: задача с id {} в {} не нашлась'.format(ident, queue_name))
        return 'NO'

    def add_task(self, queue_name, length, data):
        logging.info('--Выполняется ADD')
        queue = self.queues.get(queue_name)
        if not queue:
            self.queues[queue_name] = deque()
            queue = self.queues.get(queue_name)
        task = Task(length, data, queue)
        queue.append(task)
        logging.info('---Состояние: ' + str(self.queues))
        self.write_changed_state()
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
            while True:
                data = current_connection.recv(2048)
                message = bytes.decode(data)
                if not message:
                    logging.info('Сервер закончил работу')
                    logging.info('---Состояние: ' + str(self.queues))
                    self.write_changed_state()
                    current_connection.shutdown(1)
                    current_connection.close()
                    logging.info('='*20)
                    return
                logging.info('-На сервер пришла команда: ' + message)
                message = bytes.decode(data).split()
                command = message[0]
                args = message[1:]
                func = self.command.get(command)
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
