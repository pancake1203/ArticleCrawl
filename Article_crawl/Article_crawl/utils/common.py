
import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(str):
    match = re.match(".*?(d+).*", str)
    if match:
        return int(match.group(1))
    else:
        return 0