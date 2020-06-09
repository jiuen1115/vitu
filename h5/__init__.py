import threading
import time

from vitu.configuration import Config
from exceptions import CannotOpenH5dfError
from h5 import file
import os
import logging
import atexit

lock = threading.Lock()

cached_open_files = dict()

@atexit.register
def atexit_fun():
    print('i am exit, stack track:')
    for p in cached_open_files:
        try:
            cached_open_files[p].destroy()
        except Exception:
            pass


def __prepare(exchange, symbol, freq, year):
    p = __get_path(exchange, symbol, freq, year)
    last_p = __get_path(exchange, symbol, freq, int(year)-1)
    lock.acquire()
    global cached_open_files
    if last_p in cached_open_files:
        try:
            cached_open_files[last_p].destroy()
            del cached_open_files[p]
        except Exception:
            pass
    try:
        while True:
            try:
                f = file.File(p, lock=lock, mode='a')
                f.get_create_ohlcv(freq)
                f.swmr_mode = True

                cached_open_files[p] = f
                return
            except Exception as e:
                time.sleep(2)
                logging.warn(f"Retrying to open file {p}")
    finally:
        lock.release()


def __get_path(exchange, symbol, freq, year):
    dir = Config.h5_root_dir() + '/' + exchange.lower() + '/' + freq.lower() + '/' + symbol.replace('/', '')
    # dir=dir.lower()
    if not os.path.exists(dir):
        os.makedirs(dir, 0o755)
    return dir + '/' + str(year)


# def get_file_w(exchange, symbol, freq, year):
#     p = __get_path(exchange, symbol, freq, year)
#     if p not in cached_open_files:
#         __prepare(exchange, symbol, freq, year)
#     return cached_open_files[p]

def get_file_w(exchange, symbol, freq, year):
    p = __get_path(exchange, symbol, freq, year)
    lock.acquire()
    retry = 10
    try:
        while retry:
            try:
                f = file.File(p, lock=lock, mode='a')
                f.get_create_ohlcv(freq)
                f.swmr_mode = True

                cached_open_files[p] = f
                return f
            except Exception as e:
                time.sleep(1)
                retry -= 1
                if retry:
                    logging.warn(f"Retrying to open file {p}")
                else:
                    raise CannotOpenH5dfError(f"Cannot open file {p}")
    finally:
        lock.release()

def remove(exchange, symbol, freq, year):
    p = __get_path(exchange, symbol, freq, year)
    os.remove(p)

def recover_copy(exchange, symbol, freq, year):
    p = __get_path(exchange, symbol, freq, year)
    logging.warn(f'Recover copy {p}')
    retry = 10
    while retry:
        try:
            f1 = file.File(p, mode='r', swmr=True)
            try:
                data = f1.get_ohlcv()[0:]
                f = file.File(p + "_c", mode='a')
                f.create_dataset(data=data)
                f.close()
                os.rename(p+'_c', p)
                return
            finally:
                f1.close()
        except Exception as e:
            time.sleep(1)
            retry -= 1
            if retry:
                logging.warn(f"Retrying to copy file {p}")
            else:
                raise CannotOpenH5dfError(f'Can not copy {p}')


def get_file_r(exchange, symbol, freq, year):
    p = __get_path(exchange, symbol, freq, year)
    retry = 5
    while retry:
        try:
            f = file.File(p, mode='r', swmr=True)
            return f
        except Exception:
            time.sleep(1)
            retry -= 1
    try:
        f = file.File(p, mode='r', swmr=True)
        return f
    except Exception as e:
        raise e


if __name__ == '__main__':
    # f = get_file_w('poloniex', 'btcusdt', '5m', 2018)
    # f.close()

    recover_copy('poloniex', 'btcusdt', '1d', 2018)
