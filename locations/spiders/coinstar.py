import re
from urllib.parse import urljoin

from scrapy import Spider
from scrapy.http import JsonRequest

from locations.dict_parser import DictParser
from locations.geo import country_iseadgg_centroids


class CoinstarSpider(Spider):
    name = "coinstar"
    item_attributes = {"brand": "Coinstar", "brand_wikidata": "Q5141641"}
    start_urls = ["https://www.coinstar.com/findakiosk"]
    max_results = 1000

    def parse(self, response):
        s = response.xpath("//script[contains(text(), 'csApiToken')]/text()").get()
        api_url = re.search(r"csApiUrl\s*=\s*'([^']*)';", s).group(1)
        api_token = re.search(r"csApiToken\s*=\s*'([^']*)';", s).group(1)
        for lat, lon in country_iseadgg_centroids(["ca", "de", "es", "fr", "gb", "ie", "it", "us"], 158):
            yield JsonRequest(
                urljoin(api_url, "kiosk_selector"),
                data={"radius": 100, "total_kiosks": self.max_results, "latitude": lat, "longitude": lon},
                callback=self.parse_kiosks,
                headers={"X-AUTH-TOKEN": api_token, "Accept": "*/*"},
            )

    def parse_kiosks(self, response):
        j = response.json()
        if j["status"] != "000":
            self.logger.error(j.get("status_text"))
            return

        kiosks = j["data"]
        if len(kiosks) >= self.max_results:
            raise RuntimeError("Results truncated, need to use a larger max_results.")

        for kiosk in kiosks:
            item = DictParser.parse(kiosk)
            item["ref"] = kiosk["machine_placement_id"]
            item["located_in"] = kiosk["banner_name"]
            item["street_address"] = kiosk["street_address_text"]
            item["state"] = kiosk["state_province_code"]
            item["website"] = f"https://coinstar.com/kiosk-info?KioskId={kiosk['machine_placement_id']}"
            yield item
