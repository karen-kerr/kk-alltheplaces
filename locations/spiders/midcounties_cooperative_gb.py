from scrapy import Spider

from locations.categories import Categories, apply_category
from locations.dict_parser import DictParser
from locations.hours import DAYS_FULL, OpeningHours
from locations.pipelines.address_clean_up import clean_address


class MidcountiesCooperativeGBSpider(Spider):
    name = "midcounties_cooperative_gb"
    item_attributes = {
        "brand": "Your Co-op",
        "operator": "Midcounties Co-operative",
        "operator_wikidata": "Q6841138",
    }
    start_urls = ["https://www.midcounties.coop/static/js/stores.json"]
    no_refs = True

    def parse(self, response):
        for store in response.json()["stores"]:
            item = DictParser.parse(store)
            item["street_address"] = clean_address(
                [store.get("addressLine1"), store.get("addressLine2"), store.get("addressLine3")]
            )

            item["opening_hours"] = OpeningHours()
            for day in DAYS_FULL:
                open_time = store.get(day.lower() + "Open")
                close_time = store.get(day.lower() + "Close")

                if open_time and close_time:
                    item["opening_hours"].add_range(
                        day, open_time.replace(".", ":").zfill(5), close_time.replace(".", ":").zfill(5)
                    )

            if store["tradingGroupId"] == 1:
                item["branch"] = item.pop("name")
                item["name"] = "Your Coop Food"
                item["brand_wikidata"] = "Q121084548"
                apply_category(Categories.SHOP_CONVENIENCE, item)
            elif store["tradingGroupId"] == 2:
                if "Your Co-op Travel" not in item["name"]:
                    continue  # 7 "Carrick Travel" https://carricktravel.com/about.html
                item["branch"] = item.pop("name").replace("Your Co-op Travel ", "")
                item["name"] = "Your Co-op Travel"
                item["brand_wikidata"] = "Q7726526"
                apply_category(Categories.SHOP_TRAVEL_AGENCY, item)
            elif store["tradingGroupId"] == 4:
                apply_category(Categories.KINDERGARTEN, item)
            elif store["tradingGroupId"] == 6:
                item["brand"] = "Post Office"
                item["brand_wikidata"] = "Q1783168"
                # see https://www.midcounties.coop/our-businesses/post-office/
                # "majority of these offices are located within our food stores, either in the larger supermarkets or in our convenience stores."
                # some are separate branches and should be simply Categories.POST_OFFICE, without post_office=post_partner
                # some are aspect of another shop and should use post_office=post_partner, without being marked as a standalone post office
                # as there is no way to distinguish this cases, all get both
                apply_category(Categories.POST_OFFICE.value | {"post_office": "post_partner"}, item)

            yield item
