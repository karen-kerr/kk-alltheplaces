from locations.storefinders.where2getit import Where2GetItSpider


class SmoothieKingKYUSTTSpider(Where2GetItSpider):
    name = "smoothie_king_ky_us_tt"
    item_attributes = {
        "brand_wikidata": "Q5491421",
        "brand": "Smoothie King",
    }
    api_endpoint = "https://locations.smoothieking.com/rest/getlist"
    api_key = "95B912AA-DEE4-11ED-883E-CDDDD7DDC1D0"
