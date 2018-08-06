import scrapy

import hashlib
import urllib3

urllib3.disable_warnings()


class CustoJustoSpider(scrapy.Spider):
    name = "custojusto"

    def start_requests(self):
        self._http = urllib3.PoolManager()

        urls = [
            "https://www.custojusto.pt/portugal/q/pinball?si=1&st=a"
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        entries = response.xpath("//a[contains(@data-name, 'url')]")

        for href in response.xpath("string(//ul[contains(@class, 'pagination pull-right')]/li/a/@href)"):
            yield response.follow(href, callback=self.parse)

        for entry in entries:
            link = entry.xpath("string(./@href)").extract_first()
            yield response.follow(link, callback=self.parse_article)

    def parse_article(self, response):
        img_src = response.xpath(
            "string(//img[contains(@data-seq, '0')]/@src)").extract_first()
        title = response.xpath("string(//h1)").extract_first()
        price = response.xpath(
            "string(//span[contains(@class, 'real-price')])").extract_first().strip()
        link = response.url

        hash = self._generate_hash(title, price, img_src)

        yield {
            'title': title,
            'img_src': img_src,
            'price': price,
            'link': link,
            '_id': hash
        }

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
