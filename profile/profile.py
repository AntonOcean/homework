from functools import wraps
from datetime import datetime
import logging


DEBUG = True

if DEBUG:
    logging.basicConfig(
        handlers=[logging.FileHandler('profile.log', 'w', 'utf-8')],
        level=logging.INFO,
        format='%(message)s'
    )


def profile(func):
    @wraps(func)
    def new_func(*args):
        name = str(func).split()[1]
        print('"{}" started'.format(name))
        start_time = datetime.now().timestamp()
        result = func(*args)
        end_time = datetime.now().timestamp()
        delta = int(end_time - start_time)
        print('"{}" finished in {}s'.format(name, delta))
        logging.info('Функция {} обработана\n{}'.format(func, '=' * 20))
        return result
    return new_func


def profile_all(klass):
    for attr_name in klass.__dict__:
        attr = getattr(klass, attr_name)
        if callable(attr):
            logging.info('Метод {} класса {} обернут\n{}'.format(attr, klass, '=' * 20))
            setattr(klass, attr_name, profile(attr))
    return klass
