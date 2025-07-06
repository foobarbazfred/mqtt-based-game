import machine
import time
import hashlib

def get_uniq_id(prefix='', length=8):
    uniq_id = machine.unique_id().hex() + str(time.time()) + str(time.ticks_ms())
    sha = hashlib.sha256(uniq_id).digest().hex()
    if length > len(sha):
        uniq_id = prefix + sha
    else:
        uniq_id = prefix + sha[:length]

    return uniq_id


def timestamp():
    epoch = time.time()
    jst = epoch + 9 * 60 * 60
    (YY, MM, DD, hh, mm, ss, _, _) = time.localtime(jst)
    return f'{YY:02}/{MM:02}/{DD:02}T{hh:02}:{mm:02}:{ss:02}+09:00'


