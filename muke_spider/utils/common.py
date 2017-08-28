# -*- coding:utf-8 -*-
__author__ = 'Xie Zhaoheng'
__date__ = '2017/8/22 11:51'

import hashlib


def get_md5(url):
    if isinstance(url, str):
        url = url.encode('utf-8')
    m = hashlib.md5(url)
    m.update(url)
    return m.hexdigest()


if __name__ == '__main__':
    url = 'http://www.baidu.com/'
    print(get_md5(url))

    a = ['I', 0, 0, 0, 0, 0]
    print(a.__len__())
