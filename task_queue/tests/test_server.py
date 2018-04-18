from unittest import TestCase

from socket import *
from multiprocessing import Process
from time import sleep
import os

from server import Server


class FirstServerTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        for file in os.listdir(os.path.dirname(__file__)):
            if file.startswith('last_state') or file.startswith('server.log'):
                os.remove(file)
        super(FirstServerTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.time_limit = 0.2
        self.process = Process(target=Server, args=(8080, self.time_limit))
        self.process.start()
        host = '127.0.0.1'
        port = 8080
        addr = (host, port)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_socket.connect(addr)

    def send_command_get_answer(self, command):
        command = str.encode(command)
        self.tcp_socket.send(command)
        answer = self.tcp_socket.recv(1024)
        answer = bytes.decode(answer)
        return answer

    def test_add_command(self):
        command = 'ADD test_queue 20 808080'
        task1_id = self.send_command_get_answer(command)
        self.assertEqual(len(task1_id), 32)

        command = 'ADD test_queue 30 909090'
        task2_id = self.send_command_get_answer(command)
        self.assertEqual(len(task2_id), 32)

        command = 'ADD test_queue 20'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'Not valid command')

        command = 'IN test_queue {}'.format(task1_id)
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'YES')

        command = 'IN test_queue 5'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'NO')

        command = 'GET test_queue'
        answer = self.send_command_get_answer(command)
        self.assertListEqual(answer.split()[1:], ['20', '808080'])

        command = 'GET test_queue'
        answer = self.send_command_get_answer(command)
        self.assertListEqual(answer.split()[1:], ['30', '909090'])

        sleep(self.time_limit*60)

        command = 'IN test_queue {}'.format(task1_id)
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'YES')

        command = 'IN test_queue {}'.format(task2_id)
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'YES')

        command = 'GET test_queue'
        answer = self.send_command_get_answer(command)
        self.assertListEqual(answer.split()[1:], ['20', '808080'])

        command = 'ACK test_queue {}'.format(task1_id)
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'YES')

        command = 'IN test_queue {}'.format(task1_id)
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'NO')

        self.tcp_socket.close()
        self.process.join(1)
        self.process.terminate()


class SecondServerTestCase(TestCase):
    def setUp(self):
        self.process = Process(target=Server, args=(8080, 0.2))
        self.process.start()
        host = '127.0.0.1'
        port = 8080
        addr = (host, port)
        self.tcp_socket = socket(AF_INET, SOCK_STREAM)
        self.tcp_socket.connect(addr)

    def send_command_get_answer(self, command):
        command = str.encode(command)
        self.tcp_socket.send(command)
        answer = self.tcp_socket.recv(1024)
        answer = bytes.decode(answer)
        return answer

    def test_com(self):
        command = 'ADD test_queue 50 909090'
        answer = self.send_command_get_answer(command)
        self.assertEqual(len(answer), 32)

        command = 'GET test_queue'
        answer = self.send_command_get_answer(command)
        self.assertListEqual(answer.split()[1:], ['30', '909090'])

        self.tcp_socket.close()
        self.process.join(1)
        self.process.terminate()
