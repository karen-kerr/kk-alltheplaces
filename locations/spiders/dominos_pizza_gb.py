from scrapy.spiders import SitemapSpider

from locations.structured_data_spider import StructuredDataSpider
from locations.user_agents import BROWSER_DEFAULT


class DominosPizzaGBSpider(SitemapSpider, StructuredDataSpider):
    name = "dominos_pizza_gb"
    item_attributes = {"brand": "Domino's", "brand_wikidata": "Q839466"}
    sitemap_urls = ["https://www.dominos.co.uk/pizza-near-me/sitemap.xml"]
    sitemap_rules = [(r"https:\/\/www\.dominos\.co\.uk\/pizza-near-me\/[-.\w]+\/([-.\w\/]+)$", "parse_sd")]
    drop_attributes = ["image"]
    user_agent = BROWSER_DEFAULT
    requires_proxy = True
