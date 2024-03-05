import scrapy
import pdb
from scrapy.loader import ItemLoader
from scrapy.http import Request
from scrapy.spiders import Spider
from urllib.parse import urlparse
from joolz.items import Manual, ManualLoader

class ProductsSpider(scrapy.Spider):
    name = "Products"
    allowed_domains = ["www.joolz.com"]
    start_urls = ["https://www.joolz.com/global/en/home"]

    def parse(self, response):
        # Extracting shop links from footer
        shop_links = response.css('.jlz-nav-main a')
        
        filtered_links = []

        for link in shop_links:
            link_text = link.css('span::text').get().strip()
            if link_text != 'About Joolz':
                href = link.css('::attr(href)').get()
                new_href = "https://www.joolz.com/" + href
                filtered_links.append(new_href)
                print(link)
        # Follow each shop link
        for link in filtered_links:
            yield scrapy.Request(url=link, callback=self.parse_products)

    def parse_products(self, response):
        # Extract unique product URLs
        product_urls = response.css('div.product a::attr(href)').getall()

        filtered_urls = []

        for product_url in product_urls:
            product_href = "https://www.joolz.com/" + product_url
            filtered_urls.append(product_href)

        for product in filtered_urls:
            yield scrapy.Request(url=product, callback=self.parse_product_details)

    def parse_product_details(self, response):
        # pdb.set_trace()
        product_text = response.css('.breadcrumbs__wrapper .breadcrumbs__item:nth-child(2) a::text').get().strip()
        product_image_url = response.css('picture.jlz-wrapper__images-slide-picture source::attr(data-srcset)').get().strip()
        title_text = response.css('h1.jlz-pdp--title::text').get().strip()
        title_parts = title_text.split(' ', 1)
        parsed_url = urlparse(response.url)
        domain = parsed_url.netloc.replace("www.", "")
        file_type = response.css('div.help__section--manual p::text').get().strip().capitalize()
        files_urls =  response.css('div.help__section--manual a::attr(href)').getall()


        loader = ManualLoader(item=Manual(), response=response)
        loader.add_value('model', title_parts[1])
        loader.add_value('model_2', domain)
        loader.add_css('brand', title_parts[0])
        loader.add_value('product', product_text)
        loader.add_value('product_parent', " ")
        loader.add_value('product_lang', "en")
        loader.add_value('file_urls', files_urls)
        loader.add_value('eans', " ")
        loader.add_value('files', files_urls)
        loader.add_value('type', file_type)
        loader.add_css('url', 'link[rel="canonical"]::attr(href)')
        loader.add_value('thumbs', product_image_url)
        loader.add_value('source', response.url)

        yield loader.load_item()