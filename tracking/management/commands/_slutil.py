import time


def timestamp():
    return f'[{time.strftime("%H:%M:%S", time.localtime())}] '

def tprint(msg):
    print(timestamp() + msg)
