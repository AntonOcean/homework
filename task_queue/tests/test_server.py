from unittest import TestCase

from socket import *
from multiprocessing import Process
from time import sleep
import os

from task_queue.server import Server


class ServerTestCase(TestCase):
    def __init__(self, *args, **kwargs):
        for file in os.listdir(os.path.dirname(__file__)):
            if file.startswith('last_state'):
                os.remove(file)
        super(ServerTestCase, self).__init__(*args, **kwargs)

    def setUp(self):
        self.process = Process(target=Server)
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
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, '0')

        command = 'ADD test_queue 30 909090'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, '1')

        command = 'ADD test_queue 20'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'Not valid command')

        command = 'IN test_queue 0'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'YES')

        command = 'IN test_queue 5'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'NO')

        command = 'GET test_queue'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, '0 20 808080')

        command = 'GET test_queue'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, '1 30 909090')

        sleep(6)

        command = 'IN test_queue 0'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'YES')

        command = 'IN test_queue 1'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'YES')

        command = 'GET test_queue'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, '0 20 808080')

        command = 'ACK test_queue 0'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'ok')

        command = 'IN test_queue 0'
        answer = self.send_command_get_answer(command)
        self.assertEqual(answer, 'NO')

        self.tcp_socket.close()
