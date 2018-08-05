import scrapy
import hashlib
import urllib3
from bs4 import BeautifulSoup

urllib3.disable_warnings()


class OlxSpider(scrapy.Spider):
    name = "olx"

    def start_requests(self):
        self._http = urllib3.PoolManager()

        urls = [
            'https://www.olx.pt/ads/q-pinball/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        entries = response.xpath(
            "//table[contains(@id, 'offers_table')]/tbody/tr[contains(@class, 'wrap')]")

        for entry in entries:
            img_src = entry.xpath('string(.//img/@src)').extract_first()

            strong_tag = entry.xpath('.//strong')
            title = strong_tag[0].xpath('string(.)').extract_first()
            price = strong_tag[1].xpath('string(.)').extract_first()

            link = entry.xpath(
                "string(.//a[contains(@class, 'detailsLink')]/@href)").extract_first()

            hash = self._generate_hash(title, price, img_src)

            yield {
                'title': title,
                'img_src': img_src,
                'price': price,
                'link': link,
                '_id': hash
            }

        for href in response.xpath("string(//a[contains(@data-cy, 'page-link-next')]/@href)"):
            yield response.follow(href, callback=self.parse)

    def _generate_hash(self, title, price, img_src):
        hasher = hashlib.sha1()

        # Hash title.
        hasher.update(title.encode())

        # Hash price.
        hasher.update(price.encode())

        # Hahs image.
        request = self._http.request('GET', img_src, preload_content=False)
        for chunk in request.stream(hasher.block_size):
            hasher.update(chunk)

        request.release_conn()

        return hasher.hexdigest()
