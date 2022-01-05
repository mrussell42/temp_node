#!/usr/bin/env python
import subprocess
import argparse

DEV = '/dev/ttyUSB0'
FILES = ['boot.py', 'main.py', 'wificonf.py']


def main(files):
    """
    Main upload function
    """
    print("Files:", files)
    if files[0] is None:
        files = FILES

    for file_name in files:
        print(f"Uploading {file_name}")
        runcmd = ['ampy', '-p', DEV, '-b', '115200', 'put', file_name]
        subprocess.check_call(runcmd)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', default=None, nargs='?')
    args = parser.parse_args()
    main([args.file])
