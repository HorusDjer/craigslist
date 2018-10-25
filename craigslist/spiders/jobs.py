# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request


class JobsSpider(scrapy.Spider):
    name = 'jobs'
    allowed_domains = ['newyork.craigslist.org']
    start_urls = ['http://newyork.craigslist.org/search/egr']

    def parse(self, response):
        listings = response.xpath('//li[@class="result-row"]')
        for listing in listings:
            date = listing.xpath('//*[@class="result-date"]/@datetime').extract_first()
            link = listing.xpath('.//a[@class="result-title hdrlnk"]/@href').extract_first()
            text = listing.xpath('.//a[@class="result-title hdrlnk"]/text()').extract_first()

            yield Request(link,
                          callback=self.parse_listing,
                          meta={'date': date,
                                'link': link,
                                'text': text})
        
        next_page = response.xpath('//*[@title="next page"]/@href').extract_first()
        abs_next_page = response.urljoin(next_page)
        
        if abs_next_page is not None:
            yield Request(abs_next_page, callback=self.parse)
    
    def parse_listing(self, response):
        date = response.meta['date']
        link = response.meta['link']
        text = response.meta['text']

        compensation = response.xpath('//*[@class="attrgroup"]/span/b/text()').extract()[0]
        employment_type = response.xpath('//*[@class="attrgroup"]/span/b/text()').extract()[1]

        images = response.xpath('//*[@id="thumbs"]//@src').extract()
        images = [image.replace('50x50c','600x450') for image in images]

        address = response.xpath('//*[@id="postingbody"]/text()').extract()

        yield {
            'date': date,
            'link': link,
            'text': text,
            'compensation': compensation,
            'employment_type': employment_type,
            'images': images,
            'address': address
        }
        