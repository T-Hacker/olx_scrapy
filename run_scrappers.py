import os
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

feed_file = "olx_feed.jl"

if os.path.exists(feed_file):
    os.remove(feed_file)

process = CrawlerProcess(get_project_settings())

# 'followall' is the name of one of the spiders of the project.
process.crawl('olx')
process.crawl('custojusto')
process.start()  # the script will block here until the crawling is finished
