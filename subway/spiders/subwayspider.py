# -*- coding: utf-8 -*-
import scrapy
from scrapy.selector import Selector
from scrapy.http import Request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from subway.items import SubwayItem
import time
from lxml.html import  fromstring
from datetime import  datetime
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

class SubwayspiderSpider(scrapy.Spider):
    name = "subwayspider"
    allowed_domains = ["subway.com"]
    start_urls = (
        'https://order.subway.com/?utm_source=desktop&utm_medium=utilitynav&utm_campaign=order',
    )

    def __init__(self):
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def spider_closed(self, spider):
        print "spider is closed"
      # second param is instance of spder about to be closed.

    def parse(self, response):
        driver = webdriver.Chrome("c://chromedriver.exe")
        item = SubwayItem()
        item["TodayDate"] = datetime.now()
        import yaml
        config = yaml.safe_load(open("orders.yml"))
        restaurants = config[0]["restaurant_no"]
        locations = str(config[0]["locations"]).split(",")
        for location in locations:
            try:
                driver.get("https://order.subway.com/Stores/Find.aspx")
                search_elem = driver.find_element_by_id("txtCityName")
                search_elem.clear()
                search_elem.send_keys("64506")
                search_btn = driver.find_element_by_id("btnFindStores")
                search_btn.click()
                print "search btn clicked"
                time.sleep(5)
                address1 = driver.find_element_by_xpath('//a[@class="btnAddr1"]/h4').text
                address2 = driver.find_element_by_xpath('//div[@class="divAddr2"]').text
                item["SubwayLocation"] = address1 + address2
                print address1
                print address2
                order_btns = driver.find_elements_by_class_name("btnOrderNow")
                btn_indexes = [0]
                """
                    Restaurant no's in the searched restaurants. Iterates over the given restaurant no in the config file.
                """
                for btn_index in restaurants.split(","):
                    """
                        Subtracting 1 because because the restaurant no starts from 1 instead of 0
                    """
                    order_btns[int(btn_index)-1].click()
                    time.sleep(5)
                    order_now_btn = driver.find_element_by_class_name("btnOrderExpress")
                    order_now_btn.click()
                    print "here before sand link"
                    time.sleep(5)
                    #sandwich_link = driver.find_element_by_xpath('//h3[contains(text(),"All Sandwiches")]/../@href')
                    sandwich_link = driver.find_element_by_xpath('//li[@id="liPcg3"]')
                    sandwich_link.click()
                    print "all sandwihces 2nd link clicked"
                    time.sleep(3)
                    html = driver.page_source
                    hxs = fromstring(html)
                    all_sandwiches = hxs.xpath('//li[@class="liPcl"]/a/@href')
                    """
                        Getting all sandwich links after clicking "All Sandwiches" and iterating each link.
                    """
                    for sandwich_link in all_sandwiches:
                        print "first item clicked"
                        print sandwich_link
                        driver.get('https://order.subway.com'+sandwich_link)
                        sandwich_name = driver.find_element_by_xpath('//div[@id="divProductsPage"]/h1').text
                        if sandwich_name:
                            item["SandwichName"] = sandwich_name

                        sizes_and_prices = driver.find_elements_by_xpath('//h5[@class="hProductName"]')
                        for size_and_price in sizes_and_prices:
                            size_and_price = size_and_price.text
                            if size_and_price:
                                s_and_p = size_and_price.split("\n")
                                size = s_and_p[0]
                                import re
                                price = re.search("\$\d*\.\d*",s_and_p[1])
                                if size:
                                    item["Size"] = size
                                if price:
                                    item["Price"] = price.group()

                            yield  item

            except Exception as e:
                print e
                driver.refresh()
                #driver.get(response.url)

            raise CloseSpider("yes done")





