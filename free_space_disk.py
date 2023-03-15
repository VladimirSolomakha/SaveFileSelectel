#!/usr/bin/env python
import platform
import os
import shutil


def check_free_space(need_free_space, current_directory=None):
    GB = 10 ** 9
    disk = current_directory
    if not disk:
        disk = os.getcwd()
    result = shutil.disk_usage(disk)
    free_space = result.free/GB
    if need_free_space > 0 and free_space < need_free_space:
        return (f'Осталось {free_space:.2f} Gb  cвободного места на {disk}' +
                f' компьютера {platform.uname().node}')
    return None


if __name__ == '__main__':
    result = check_free_space(25)
    if result:
        print(result)
