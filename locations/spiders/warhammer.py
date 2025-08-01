from typing import Iterable

from scrapy.http import Response

from locations.hours import OpeningHours
from locations.items import Feature
from locations.storefinders.algolia import AlgoliaSpider


class WarhammerSpider(AlgoliaSpider):
    name = "warhammer"
    item_attributes = {"brand": "Warhammer", "brand_wikidata": "Q587270"}
    app_id = "M5ZIQZNQ2H"
    api_key = "92c6a8254f9d34362df8e6d96475e5d8"
    index_name = "prod-lazarus-store"

    def post_process_item(self, item: Feature, response: Response, feature: dict) -> Iterable[Feature]:
        item["website"] = None  # 404
        item["lat"] = feature.get("_geoloc", {}).get("lat")
        item["lon"] = feature.get("_geoloc", {}).get("lng")

        item["opening_hours"] = OpeningHours()
        for day, rule in feature.get("hours", {}).items():
            if not isinstance(rule, dict):
                continue
            if rule.get("isClosed", False):
                continue
            for time in rule.get("openIntervals", []):
                item["opening_hours"].add_range(day, time["start"], time["end"])

        if item.get("lat") is None or item["lat"] > -80:  # skips broken/joke entries
            yield item
