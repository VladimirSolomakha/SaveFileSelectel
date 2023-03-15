#!/usr/bin/env python
import boto3
import fnmatch
import logging
import os

from free_space_disk import check_free_space
from telegram_message import send_message


logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
log_name = os.path.basename(__file__) + '.log'
file_handler_log = logging.FileHandler(log_name, encoding="utf-8")
formater = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler_log.setFormatter(formater)
file_handler_log.setLevel(logging.INFO)
logger.addHandler(file_handler_log)


BUCKET_NAME = 'backupmpk_pg'
COUNT_FILES_KEEP = 5
NEED_FREE_SPACE = 30


def write_send_error(error_message):
    logger.error(error_message)
    send_message(error_message)


def autorize():
    try:
        return boto3.client(
            service_name='s3',
            endpoint_url='https://s3.storage.selcloud.ru'
            )
    except Exception as error:
        logger.error(f'Ошибка {error} авторизации на сервере!')
        return None


def upload_file(file_name):
    s3 = autorize()
    if not s3:
        return
    logger.info(f'Начинаем попытку отправки файла {file_name}')
    try:
        s3.upload_file(file_name, BUCKET_NAME, file_name)
    except Exception as error:
        write_send_error(f'Ошибка {error} загрузки {file_name} на сервер!')
        return False
    logger.info(f'Загрузили файл {file_name} на сервер')
    return True


def check_file(file_name, file_size, write_log=True):
    s3 = autorize()
    if not s3:
        return
    # проверить что Contents есть
    for key in s3.list_objects(Bucket=BUCKET_NAME)['Contents']:
        if key.get('Key') == file_name:
            if write_log:
                logger.info(f'Файл {file_name} присутствует в хранилище')
            file_size_server = key.get('Size')
            if file_size_server != file_size:
                if write_log:
                    write_send_error(f'Отличается размер файла {file_name}! На'
                                     ' диске {file_size}, в хранилище '
                                     '{file_size_server}')
                return False
            return True
    if write_log:
        write_send_error(f'Ошибка, файл {file_name} отсутствует на сервере!')
    return False


def handle_mask_file(file_mask):
    sort_files = []
    current_dir = os.path.dirname(__file__)
    for _, _, files in os.walk(current_dir):
        for file in files:
            if file in fnmatch.filter(files, file_mask):
                sort_files.append(file)
    sort_files.sort(reverse=True)
    count_files_handled = 0
    delete_files = []
    for cur_file in sort_files:
        if count_files_handled >= COUNT_FILES_KEEP:
            os.remove(f'{current_dir}//{cur_file}')
            delete_files.append({'Key': cur_file})
            continue
        file_size = os.stat(cur_file).st_size
        if file_size == 0:
            write_send_error(f'Ошибка, файл {cur_file} имеет нулевой размер ' +
                             'и будет пропущен!')
            continue
        if not check_file(cur_file, file_size, False):
            upload_file(cur_file)
            check_file(cur_file, file_size)
        count_files_handled += 1
    if len(delete_files) > 0:
        s3 = autorize()
        if not s3:
            return
        try:
            s3.delete_objects(Bucket=BUCKET_NAME,
                              Delete={'Objects': delete_files})
        except Exception as error:
            logger.error(f'Ошибка удаления старых файлов на сервере {error}')


if __name__ == '__main__':
    free_space_checking_error = check_free_space(NEED_FREE_SPACE)
    if free_space_checking_error:
        write_send_error(free_space_checking_error)
    file_bases = open('bases.txt', 'r')
    lines_file_bases = file_bases.readlines()
    for current_file_mask in lines_file_bases:
        handle_mask_file(current_file_mask.strip())
