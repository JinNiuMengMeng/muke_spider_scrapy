# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from muke_spider.utils.JsonMy import CJsonEncoder
import codecs
import json
from scrapy.exporters import JsonItemExporter
import MySQLdb
import MySQLdb.cursors
import os
from twisted.enterprise import adbapi


class MukeSpiderPipeline(object):
    def process_item(self, item, spider):
        return item


class JsonWithEncodingPipeline(object):
    # 方法一：自定义输出json文件方法

    def __init__(self):
        """
        第一步：先打开一个json文件，这里使用codecs的原因是因为codecs能够解决复杂的编码问题
        """
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        """
        第二步：json处理item
        参数一：将item转换成字符串，这里使用json方法，json方法可以将字典转换成字符串，所以先将item转换成字典
        参数二：ensure_ascii=False 是为了解决写入中文乱码的问题 
        参数三：cls，指定自定义的json处理函数，因为默认的json处理函数无法将datetime.date格式的时间转换成json格式
        """
        lines = json.dumps(dict(item), ensure_ascii=False, cls=CJsonEncoder) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        """
        第三步：关闭打开的json文件
        """
        self.file.close()


class JsonExporterPipeline(object):
    # 方法二：调用scrapy提供的json export导出json文件
    def __init__(self):
        self.file = open('articleexport.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class MysqlPipeline(object):
    """
    方法一：自定义方法写入数据到数据库
    """
    def __init__(self):
        """
        第一步： 打开数据库连接
        第二步： 使用cursor()方法获取操作游标 
        第三步： 使用execute方法执行SQL语句
        第四步： 提交到数据库执行
        """
        self.conn = MySQLdb.connect("127.0.0.1", "root", "123456", "muke_spider", charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursors()

    def process_item(self, item, spider):
        insert_sql = """
            insert into article(title, create_date, url, url_object_id, front_image_url, front_image_path, praise_nums, comment_nums, fav_nums, tags)
            VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        self.cursor.execute(insert_sql, (item['title'], item['create_date'], item['url'], item['url_object_id'], item['front_image_url'][0], item['front_image_path'], item['praise_nums'], item['comment_nums'], item['fav_nums'], item['tags']))
        self.conn.commit()


class MysqlTwistedPipeline(object):
    """
    twisted 内部提供了一个异步容器，连接池，可供调用
    twisted中的 adbapi 可以将 Mysqldb 操作变成异步操作
    """
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        """
        参数setting就是该spider的srtting文件，在此可以方便的取出setting中的值
        """
        dbparms = dict(
            host = settings['MYSQL_HOST'],
            db = settings['MYSQL_DBNAME'],
            user = settings['MYSQL_USER'],
            passwd = settings['MYSQL_PASSWORD'],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error) #处理异常

    def handle_error(self, failure):
        # 处理异步插入的异常
        print(failure)

    def do_insert(self, cursor, item):
        # 执行具体的插入
        insert_sql = """
            insert into article(title, create_date, url, url_object_id, front_image_url, front_image_path, praise_nums, comment_nums, fav_nums, tags)
            VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_sql, (
        item['title'], item['create_date'], item['url'], item['url_object_id'], item['front_image_url'][0],
        item['front_image_path'], item['praise_nums'], item['comment_nums'], item['fav_nums'], item['tags']))


class ArticleImagePipelines(ImagesPipeline):
    """
    重载ImagesPipeline中的item_completed方法，获取文件保存的路径
    """
    image_guid = ""
    images_path = os.path.abspath('images')
    def item_completed(self, results, item, info):
        for ok, value in results:
            image_file_path = value['path']
            self.path = image_file_path
            item['front_image_path'] = self.path
            return item

    # 重载ImagesPipeline中的file_path方法，重命名图片名称，使用原始文件名
    def file_path(self, request, response=None, info=None):
        self.image_guid = request.url.split('/')[-1]
        # return 'full/%s.jpg' % (image_guid)
#        return 'BoLe_Picture\%s' % (self.image_guid)
        return os.path.join(self.images_path, 'BoLe_Picture\%s'%(self.image_guid))

if __name__ == "__main__":
    images_path = os.path.abspath('images')
    print(os.path.join(images_path, 'BoLe_Picture\%s'%(ArticleImagePipelines.image_guid)))


"""
project_dir = os.path.abspath(os.path.dirname(__file__))
IMAGES_STORE = os.path.join(project_dir, 'images')
"""