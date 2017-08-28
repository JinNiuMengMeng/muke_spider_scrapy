# -*- coding:utf-8 -*-
__author__ = 'Xie Zhaoheng'
__date__ = '2017/8/17 14:10'

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
#execute(["scrapy", "crawl", "jobbole", "--nolog"])
execute(["scrapy", "crawl", "jobbole"])

