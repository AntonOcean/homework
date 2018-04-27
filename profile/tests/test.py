from unittest import TestCase
from profile import profile
from time import sleep


class DictTestCase(TestCase):
    def test_func(self):

        @profile
        def function_test():
            sleep(2)

        function_test()

        @profile
        class TestClass:
            def __init__(self):
                self.method()

            def method(self):
                sleep(1)

        test = TestClass()
        test.method()