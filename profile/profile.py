from functools import wraps
from datetime import datetime
from time import sleep
import logging


DEBUG = True


def debug():
    logging.basicConfig(
        handlers=[logging.FileHandler('profile.log', 'w', 'utf-8')],
        level=logging.INFO,
        format='%(message)s'
    )


def profile(obj):
    global DEBUG
    if DEBUG:
        debug()
        DEBUG = False
    class_name = type(obj).__name__
    logging.info('Обрабатывается: {}'.format(obj))
    if class_name != 'function':
        for attr_name in obj.__dict__:
            attr = getattr(obj, attr_name)
            if callable(attr):
                logging.info('Метод {} класса {} обернут\n{}'.format(attr, obj, '='*20))
                setattr(obj, attr_name, profile(obj.__dict__[attr_name]))
        return obj
    else:
        @wraps(obj)
        def new_func(*args):
            name = str(obj).split()[1]
            print('"{}" started'.format(name))
            start_time = datetime.now().timestamp()
            result = obj(*args)
            end_time = datetime.now().timestamp()
            delta = int(end_time - start_time)
            print('"{}" finished in {}s'.format(name, delta))
            logging.info('Функция {} обработана\n{}'.format(obj, '='*20))
            return result
        return new_func


if __name__ == '__main__':
    @profile
    def functio():
        sleep(1)

    functio()

    @profile
    class Bar:
        def __init__(self):
            self.name = 'default'
            self.method()
            sleep(1)

        def method(self):
            sleep(1)
            self.name = 'hello'

    x = Bar()
    x.method()
