
import hashlib
import re


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()


def extract_num(text):
    match = re.match(".*?(\d+).*", text)
    if match:
        num = int(match.group(1))
    else:
        num = 0
    return num


def remove_num_dot(text):
    num_list = text.split(',')
    num = int("".join(num_list))
    return num