# -*- coding:utf-8 -*-
__author__ = 'Xie Zhaoheng'
__date__ = '2017/8/23 15:43'
import json
import datetime
import decimal
import os

class CJsonEncoder(json.JSONEncoder):
    """
    如果时间类型是 datetime.date 或者 str 类型，指定该方法处理
    """
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            #return obj.strftime('%Y-%m-%d %H:%M:%S')
            return obj.strftime('%Y-%m-%d')
        elif isinstance(obj, datetime.date):
            return obj.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, obj)


if __name__ == "__main__":
    # item时间类型是 datetime.date
    item = {'comment_nums': 0, 'create_date': datetime.date(2017, 8, 3)}
    lines = json.dumps(dict(item), ensure_ascii=False, cls=CJsonEncoder) + "\n"
    print('lines: ', lines)

    # item时间类型是 str
    item_2 = {'comment_nums': 3, 'create_date': '2017/8/3'}
    lines_2 = json.dumps(dict(item), ensure_ascii=False, cls=CJsonEncoder) + "\n"
    print('lines_2: ', lines_2)
