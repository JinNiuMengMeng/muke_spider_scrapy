# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy.http import Request
import datetime
from urllib import parse
from muke_spider.items import JobboleArticleItem
from muke_spider.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['python.jobbole.com']
    start_urls = ['http://python.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1. 获取文章列表页中的文章url，并交给Scrapy下载后进行解析
        2. 获取下一页的url并交给scrapy下载，下载完成后交给parse
        """

        """1.解析列表页中的所有文章url以及图片链接，并交给scrapy下载后进行解析
        """
        get_urls = response.xpath('//div[@class="post-thumb"]/a')
        for urls in get_urls:
            img_urls = urls.xpath('img/@src').extract()[0]
            post_url = urls.xpath('@href').extract()[0]
            yield Request(url=(parse.urljoin(response.url, post_url)), meta={"front_image_url":img_urls}, callback=self.parse_detail)

        """提取下一页的url连接"""
        next_url = response.xpath('//a[@class="next page-numbers"]/@href').extract()[0]
        if next_url:
            yield Request(url=(parse.urljoin(response.url, next_url)), callback=self.parse)
        else:
            print('爬虫完毕')

    def parse_detail(self, response):
        article_Item = JobboleArticleItem()
        """
        提取文章的详细信息
        response.xpath('//div[@class="entry-header"]/h1').extract()[0]
        """
        article_title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]
        article_Data = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/text()').extract()[0].strip().replace("·", '')

        print('标　题：', article_title)
        print('时　间：', article_Data)
        print('文章链接：', response.url)

        """获取封面图链接
        使用get方法获取字典中的元素，如果失败，不会中断程序抛出异常
        """
        front_image_url = response.meta.get('front_image_url', '')
        print('封面图：', front_image_url)

        """抽取点赞数，如果没有人点赞，将其设置为0"""
        article_praise = response.xpath('//*[@class="post-adds"]/span/h10/text()').extract()[0]
        if article_praise:
            article_praise = int(article_praise)
        else:
            article_praise = 0
        print('点赞数：', article_praise)

        """抽取收藏数，如果没有人收藏，将其设置为0"""
        article_collect = response.xpath('//*[@class="post-adds"]/span[2]/text()').extract()[0]
        collect_num_ = re.match('.*(\d+).*', article_collect)#匹配收藏的数字
        if collect_num_:
            collect_num = int(collect_num_.group(1))
        else:
            collect_num = 0
        print('收藏数：', collect_num)

        """抽取评论数，如果没有人评论，将其设置为0   a[@href="#article-comment"]>"""
        article_comment = response.xpath('//a[@href="#article-comment"]/span/text()').extract()[0]
        comment_num_ = re.match('.+(\d+).+', article_comment)
        if comment_num_ is None:
            comment_num = 0
        else:
            comment_num = int(comment_num_.group(1))
        print('评论数：', comment_num)

        """抽取tag标签 """
        article_tag = response.xpath('//*[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tag_list = [article_tag_ for article_tag_ in article_tag if not article_tag_.strip().endswith('评论')]
        tags = ', '.join(tag_list)
        print('文章标签：', tags)
        print('\n')

        """文章正文"""
        #article_content = response.xpath('//*[@class="entry"]').extract()[0]

        article_Item['title'] = article_title
        print()
        try:
            article_data = datetime.datetime.strptime(article_Data.strip(), "%Y/%m/%d").date()
        except Exception as e:
            article_data = datetime.datetime.now().date()
        article_Item['create_date'] = article_data
        article_Item['url'] = response.url
        article_Item['url_object_id'] = get_md5(response.url)
        # 因为setting中IMAGES_URLS_FIELD会将front_image_url作为数组处理，因此将front_image_url用[]括起来
        article_Item['front_image_url'] = [front_image_url]
        article_Item['praise_nums'] = article_praise
        article_Item['comment_nums'] = comment_num
        article_Item['fav_nums'] = collect_num
        article_Item['tags'] = tags
        #article_Item['content'] = article_content

        # 返回我们创建的Item，系统会自动将数据返回给pipelines.py
        yield article_Item
