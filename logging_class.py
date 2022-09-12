import logging
import os
from datetime import datetime
from inspect import getframeinfo, stack
from pathlib import Path
import sys


log_name = f'{datetime.date(datetime.now()).isoformat()}.log'
log_folder = Path('logs').absolute().resolve()
if not log_folder.exists():
    log_folder.mkdir()
log_file = log_folder.joinpath(log_name).resolve()
format = '%(levelname)s - %(filename)s - %(funcName)s - %(message)s - ' \
            '%(asctime)s'


class CustomFormatter(logging.Formatter):

    def format(self, record):
        if hasattr(record, 'func_name'):
            record.funcName = record.func_name
        if hasattr(record, 'module_name'):
            record.filename = record.module_name
        return super(CustomFormatter, self).format(record)


FORMATTER = CustomFormatter(format)


class Mylog:

    @classmethod
    def get_console_handler(cls):
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomFormatter(format))
        return console_handler

    @classmethod
    def get_file_handler(cls):
        file_handler = logging.FileHandler(log_file, 'a+')
        file_handler.setFormatter(CustomFormatter(format))
        return file_handler

    @classmethod
    def get_logger(cls):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.DEBUG)
        # logger.addHandler(cls.get_console_handler())
        logger.addHandler(cls.get_file_handler())
        logger.propagate = False
        return logger


def add_log(extra):
    def inner(func):
        def wrapper(*args, **kwargs):
            name = func.__name__
            log.debug(f"started {name} method", extra=extra)
            return func(*args, **kwargs)
        return wrapper
    return inner


def my_log(cls):
    for method in dir(cls):
        if not method.startswith('__') and callable(getattr(cls, method)):
            py_file_caller = getframeinfo(stack()[1][0])
            extra = {
                'func_name': method,
                'module_name': os.path.basename(py_file_caller.filename)
            }
            cur_method = add_log(extra)(getattr(cls, method))
            setattr(cls, method, cur_method)
    return cls


log = Mylog.get_logger()

