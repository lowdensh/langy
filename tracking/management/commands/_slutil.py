import time


# Returns a string
#   representing the current time.
#   e.g. [16:27:24]
def timestamp():
    return f'[{time.strftime("%H:%M:%S", time.localtime())}] '

# Print with timestamp.
def tprint(msg):
    print(timestamp() + msg)
