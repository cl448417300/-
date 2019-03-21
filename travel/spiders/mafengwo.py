#!/usr/bin/env python
# _*_coding: utf-8 _*_
import requests
from lxml import etree
import re

from db.mongodb import mongo
"""
1：准备url列表
2：遍历url列表，发送请求，获取响应数据
3：解析数据
4：保存数据
"""


class MaFengWoSpider(object):
    def __init__(self, city):
        self.city = city
        self.url_patten = ' http://www.mafengwo.cn/search/s.php?q='+city+'&p={}&t=poi&kt=1'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/'
                          '72.0.3626.121 Safari/537.36'
        }

    def get_url_list(self):
        url_list = []
        for i in range(1, 21):
            url = self.url_patten.format(i)
            url_list.append(url)
        return url_list

    def get_page_from_url(self, url):
        response = requests.get(url, headers=self.headers)
        return response.content.decode()

    def get_datas_from_page(self, page):
        element = etree.HTML(page)
        lis = element.xpath('//*[@id="_j_search_result_left"]/div/div/ul/li')
        data_list = []
        for li in lis:
            item = {}
            name = ''.join(li.xpath('./div/div[2]/h3/a//text()'))
            # print(name)
            if name.find('景点') == -1:
                continue
            item['name'] = name.replace('景点 -', '')
            # print(item)
            item['address'] = li.xpath('./div/div[2]/ul/li[1]/a//text()')[0]
            comments_num = li.xpath('./div/div[2]/ul/li[2]/a//text()')[0]
            item['comments_num'] = int(re.findall(r'点评\((\d+)\)', comments_num)[0])
            # print(comments_num)
            travel_notes_num = li.xpath('./div/div[2]/ul/li[3]/a//text()')[0]
            item['travel_notes_num'] = int(re.findall(r'游记\((\d+)\)', travel_notes_num)[0])
            item['city'] = self.city
            # print(item)
            data_list.append(item)
        return data_list

    def save_data(self, datas):
        for data in datas:
            data['_id'] = data['name']
            mongo.save(data)

    def run(self):
        """
        1：准备url列表
        url_list = self.get_url_list()
        2：遍历url列表，发送请求，获取响应数据
        3：解析数据
        4：保存数据
        """
        url_list = self.get_url_list()
        # print(url_list)
        for url in url_list:
            page = self.get_page_from_url(url)
            datas = self.get_datas_from_page(page)
            self.save_data(datas)


if __name__ == '__main__':
    ms = MaFengWoSpider('广州')
    ms.run()