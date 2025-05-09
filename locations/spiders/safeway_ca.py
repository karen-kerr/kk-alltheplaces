from scrapy.spiders import SitemapSpider

from locations.categories import Categories, apply_category
from locations.hours import OpeningHours
from locations.items import Feature


class SafewayCASpider(SitemapSpider):
    name = "safeway_ca"
    item_attributes = {"brand": "Safeway", "brand_wikidata": "Q17111901"}
    allowed_domains = ["www.safeway.ca"]
    sitemap_urls = ("https://www.safeway.ca/store-sitemap.xml",)
    sitemap_rules = [(r"/stores/", "parse_store")]

    def parse_store(self, response):
        properties = {
            "ref": response.xpath("//@data-store-id").extract_first(),
            "name": response.xpath('//meta[@property="og:title"]/@content').extract_first(),
            "website": response.url,
            "lat": response.xpath("//@data-lat").extract_first(),
            "lon": response.xpath("//@data-lng").extract_first(),
            "addr_full": response.css(".location_address_address_1::text").extract_first(),
            "city": response.css(".city::text").extract_first(),
            "state": response.css(".province::text").extract_first(),
            "postcode": response.css(".postal_code::text").extract_first(),
            "phone": response.xpath('//a[contains(@href,"tel:")]/text()').extract_first(),
            "opening_hours": self.parse_hours(response),
        }

        item = Feature(**properties)
        apply_category(Categories.SHOP_SUPERMARKET, item)
        yield item

    def parse_hours(self, response):
        tbl = response.css(".holiday_hours_tbl")[-1].xpath("./tbody//text()")
        vals = [s for s in tbl.extract() if s.strip()]
        opening_hours = OpeningHours()
        for day, span in zip(*[iter(vals)] * 2):
            day = day[:2]
            if "Closed" in span:
                opening_hours.set_closed(day)
            else:
                span_split = span.split(" to ")
                if len(span_split) == 2:
                    open_time = span_split[0].replace("a.m.", "AM")
                    close_time = span_split[1].replace("p.m.", "PM")
                else:
                    continue
                opening_hours.add_range(day, open_time, close_time, "%I:%M %p")
        return opening_hours.as_opening_hours()
