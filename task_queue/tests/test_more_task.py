import unittest
from unittest import TestCase

import time
import socket
import os

import subprocess


class ServerMoreTaskTest(TestCase):
    def __init__(self, *args, **kwargs):
        for file in os.listdir(os.path.dirname(__file__)):
            if file.startswith('last_state') or file.startswith('server.log'):
                os.remove(file)
        super(ServerMoreTaskTest, self).__init__(*args, **kwargs)

    def setUp(self):
        self.server = subprocess.Popen(['python', 'server.py'])
        # даем серверу время на запуск
        time.sleep(0.5)

    def tearDown(self):
        self.server.terminate()
        self.server.wait()

    def send(self, command):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(('127.0.0.1', 8080))
        s.send(command)
        data = s.recv(1000000)
        s.close()
        return data

    def test_more_tasks(self):
        for i in range(200):
            command = 'ADD 2 {} 12345'.format(str(i))
            self.send(command.encode())
        task_id = self.send(b'ADD 1 5 12345')
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))
        self.assertEqual(task_id + b' 5 12345', self.send(b'GET 1'))
        self.assertEqual(b'YES', self.send(b'IN 1 ' + task_id))
        self.assertEqual(b'YES', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'ACK 1 ' + task_id))
        self.assertEqual(b'NO', self.send(b'IN 1 ' + task_id))

        self.tearDown()


if __name__ == '__main__':
    unittest.main()
