from scrapy import Spider
from scrapy.http import JsonRequest

from locations.categories import Categories, Fuel, apply_category, apply_yes_no
from locations.dict_parser import DictParser


class MarathonPetroleumUSSpider(Spider):
    name = "marathon_petroleum_us"
    brands = {
        "ARCO": {"brand": "Arco", "brand_wikidata": "Q304769"},
        "MARATHON": {"brand": "Marathon", "brand_wikidata": "Q458363"},
    }
    allowed_domains = ["devmarathon.dialogs8.com"]
    start_urls = [
        "https://devmarathon.dialogs8.com/ajax_stations_search.html?reason=get-station-info&reason=get-station-info"
    ]
    custom_settings = {"ROBOTSTXT_OBEY": False}

    def start_requests(self):
        for url in self.start_urls:
            yield JsonRequest(url)

    def parse(self, response):
        for location in response.json():
            item = DictParser.parse(location)
            item["street_address"] = ", ".join(filter(None, [location.get("addr1"), location.get("addr2")]))
            if location["site_brand"] in self.brands.keys():
                item.update(self.brands[location["site_brand"]])
            apply_category(Categories.FUEL_STATION, item)
            fuel_types_raw = list(
                map(str.upper, map(str.strip, [fuel["description"] for fuel in location.get("price_data", [])]))
            )
            fuel_types_matched = []
            for fuel_type in fuel_types_raw:
                match fuel_type:
                    case "DIESEL" | "DIESL" | "DSL" | "CAR DIESEL" | "PREM DIESE" | "OFF DIESEL" | "DSL1" | "OFFROAD" | "OFF-ROAD" | "OFFRD" | "OFF ROAD DIESEL" | "DIES" | "DIIESEL" | "#1 DIESEL" | "ON RD DSL" | "AUTO DIESEL" | "DSL #1" | "OFFDIE" | "OFF ROAD" | "OFF RD" | "CARDSL" | "AUTO DSL" | "DIESEL 1" | "OFFRDDSL" | "ONRDDSL" | "OFF RD DSL" | "ONRD" | "ORDSL" | "OFF ROAD DSL" | "OFFROAD DIESEL" | "ON RD" | "DEISEL 1" | "OFFDSL" | "OF DIE" | "ON DIE" | "OFF DSL" | "DIESEL #1" | "OFFRD DSL" | "ORDIES" | "DIESL 1" | "OFF RD DIE" | "DIESEL1" | "DSL 1" | "DS1" | "OFF-RD" | "O/R DIESEL" | "PREM DSL" | "#1 DSL" | "DIESEL1" | "DIESLE" | "OF DSL" | "OFF RD DIESEL" | "OFFRDD" | "OFF-RD" | "OFRDSL" | "ON RD DIESEL" | "ON-ROAD DIESEL" | "ON ROAD" | "ORD" | "O ROAD" | "P/DIESEL" | "PDL" | "PREM DIESEL" | "PREMIUM DIESEL" | "RNEW DSL" | "ADSL" | "CLRDSL" | "DEISEL" | "DIESE EAST" | "DIESELWEST" | "DIESEL OR" | "OFFDIESEL" | "OFFRD DIES" | "ONROAD" | "P/DSL" | "PLU DSL" | "DSLOFF" | "DSL ON" | "OFFDIESEL" | "OFF ROAD 2" | "ON ROAD DIESEL" | "PREM DSEL":
                        fuel_types_matched.append(Fuel.DIESEL)
                    case "DSL2" | "DIESEL 2" | "#2 DIESEL" | "DSL #2" | "DSL#2" | "DIESEL #2" | "DIESEL2" | "DSL 2 PREM" | "DSL 2" | "#2 DSL" | "DIE 2" | "DIESL2" | "REG DSL #2" | "DIESEL #2`" | "DIESEL 2 N" | "DIESEL 2 S":
                        fuel_types_matched.append(Fuel.COLD_WEATHER_DIESEL)
                    case "TRUCK DIESEL" | "TRK DIESEL" | "TRUCK DSL" | "TUCK DSL" | "TDSL" | "TRKDSL" | "TRK DSL":
                        fuel_types_matched.append(Fuel.HGV_DIESEL)
                    case "DSL TAX EX":
                        fuel_types_matched.append(Fuel.UNTAXED_DIESEL)
                    case "BIODSL 15%":
                        fuel_types_matched.append(Fuel.BIODIESEL)
                    case "UNLD" | "REGUNL" | "UNLEAD" | "UNLEADED" | "UNLD1" | "REGULAR" | "REG" | "REG1" | "87" | "UNLEADED FUEL" | "REG 87" | "UNLD87" | "NO ETH 87" | "UNLD 87" | "UNL" | "RUL" | "RUNL" | "REGULAR UNLEADED" | "REG UNLEADED" | "UNLEADED1" | "UNLEADED2" | "REGULAR UL" | "UNLEAD REG" | "UNLEAD 1" | "UNLEAD 2" | "UNLEAD3" | "87 OXY" | "CONV87" | "RNL" | "REGUALR" | "UNLD2" | "UNLD3" | "87NO ETH" | "87-ETHFREE" | "UNLEAD1" | "UNLEAD2" | "ULEADED" | "UNL REG" | "EC UNLD" | "EC UNLEAD" | "UNLEADED 1" | "UNLEADED 2" | "REGULAR1" | "REC FUEL" | "REGU" | "REG NL" | "UNLEADED 2" | "UNLED" | "REG 1" | "REG 2" | "UNLEADED87" | "UNLEADED REG" | "UNLEAD 87" | "STRA87" | "UNL REGULAR" | "REGULAR2" | "REG2" | "REGULAR NL" | "UNLD 1" | "CONV UNLD" | "NO UNL" | "REGNL" | "REG UNLEAD" | "87 NON" | "OXY 87" | "OXY 87 OCT" | "REGULA" | "REGULAR 1" | "REGULAR 2" | "REGUL" | "REGULR" | "REG UNLD" | "UNDLEAD" | "UNLD/REG" | "UNL E0" | "UNLEADE" | "UNLEAD ROA" | "UNLED FUEL" | "87A" | "87B" | "NOLEAD 87 OXY" | "REG NO ETH" | "REG NOLEAD" | "REGULAR 2" | "REGULAR BLD" | "REG UL" | "REGULR" | "REGUNLD" | "REG UNL" | "REG UN" | "UNLD 2" | "UNLD REG" | "UNLD/REG" | "NON UNL" | "87 CON" | "E0 UNL" | "CONV REG" | "CONV U/L" | "CONV UNL" | "NON E REG" | "NON ETHANOL REG" | "UNLD REG." | "UNLEAD87":
                        fuel_types_matched.append(Fuel.OCTANE_87)
                    case "UNLD88":
                        fuel_types_matched.append(Fuel.OCTANE_88)
                    case "MID" | "MIDGRD" | "MID GRADE1" | "MID-GRADE" | "MID1" | "PLUS" | "MIDGRADE" | "MID 1" | "MIDG" | "89" | "PLUS UNLEADED" | "UNLD PLUS" | "MID 89" | "MID89" | "PLS" | "PLUS 89" | "PLSUNL" | "UNLEAD PLS" | "PUL" | "PLUS1" | "MIDGRADE1" | "MIDGRADE2" | "PLUSUL" | "MIDGRADE 1" | "MIDGRADE 2" | "MIDGRADE3" | "PNL" | "89-ETHFREE" | "UNL PLUS" | "MNL" | "EC PLUS" | "EC UN PLUS" | "MIDGR" | "PLUS 1" | "PLUS 2" | "SUPER 89" | "MIDGRADE89" | "MID GRADE" | "MIDGRADE 89" | "PLUS2" | "MIDGADE" | "MIDGRADE`" | "NO PLUS" | "PLU" | "PLUSE" | "PLUS-EXTRA" | "PLUS+" | "PLUS UNLEA" | "MID2" | "MIDGRAD" | "MID GRD" | "MIDUNL" | "MIGRADE" | "OXY 91" | "PLU" | "PLUS E0" | "UL PLUS" | "89A" | "89B" | "MIDEGRADE" | "MIN BLEND" | "MID-GRADE UNLEADED" | "REC 89" | "UNLD MID" | "UNLEAD 89" | "UNLEADED PLUS" | "PLUS BLD" | "PLUS EXTRA" | "PLUS/MIDGR" | "PLUS UNL" | "MIDEGRADE" | "MIDGRADE UNLEADED" | "MIDGRAGE" | "NON PLUS" | "CON PLUS" | "E0 PLUS" | "MIDRGRADE" | "MID BLEND" | "PLUS3" | "PLUS BLND" | "UNLEADPLS":
                        fuel_types_matched.append(Fuel.OCTANE_89)
                    case "90EXTRA" | "REC 90" | "REC-90" | "90 EXTRA" | "REC90" | "90 REC" | "90 OCT" | "90R" | "90REC" | "CONVENTIONAL 90" | "90CONV" | "90 NONETH" | "REC 90 NO ETH" | "REG90" | "90A":
                        fuel_types_matched.append(Fuel.OCTANE_90)
                    case "PREM" | "PREMIUM" | "SUPER" | "SUPER UNLEADED" | "UNLD PREM" | "SUP" | "UNL SUP US" | "PRMUNL" | "PREMIUM UNLEADED" | "PEMIUM" | "PREMIUM1" | "PREMUL" | "PREMIUM 91" | "PREMIUM UL" | "PREM UNLEADED" | "PREMUIM" | "PREM91" | "91" | "PREMUM" | "PREMIUM2" | "91 CLR" | "PREMIEUM" | "SUPRM" | "UNL PREM" | "SNL" | "EC PREM" | "EC UN PREM" | "91NON OXY" | "PREMIUM91" | "PREMIUM OXY" | "PREMIUM  UL" | "EC PREMIUM" | "91 NON OXY" | "NO PREM" | "SUPREME" | "SUPREME+" | "SUPREME-+" | "SUP UNLEAD" | "SUPUNL" | "PREM1" | "PREM2" | "PREM DIESEL" | "PREMIUM 1" | "PREMIUM 2" | "PREM NL" | "PREMNOOXY" | "UL PREMIUM" | "UL PREM" | "UNLE PREM" | "91 NONOXY" | "PREM 91" | "PREMIOM" | "PREMIUM 91 NON-OXY" | "PREMIUM 91 OXY" | "PREMIUM NE" | "PREM UL" | "PREM UNL" | "PRE" | "REC910" | "SUPER 2" | "SUPER BLD" | "SUPER UNLD" | "UNLEAD 93" | "UNLD PRM" | "NON SUPER" | "PREMIEM" | "PREMIUNM" | "PRM" | "SUPER E0" | "SUPER FUEL" | "SUPER+" | "SUPER PREMIUM 1" | "SUPER PREM" | "SUP +":
                        fuel_types_matched.append(Fuel.OCTANE_91)
                    case "PREM92" | "92 OXY":
                        fuel_types_matched.append(Fuel.OCTANE_92)
                    case "93" | "PREM 93" | "SUP 93" | "93 OXY" | "ULTRA 93" | "ULTRA" | "93A" | "ULT" | "UNL93":
                        fuel_types_matched.append(Fuel.OCTANE_93)
                    case "REG100":
                        fuel_types_matched.append(Fuel.OCTANE_100)
                    case "REGULAR E5":
                        fuel_types_matched.append(Fuel.E5)
                    case "E10" | "ETH REG 10%" | "87-E10" | "E-10 REG" | "E-10 PLUS" | "E-10 PREM" | "E-10" | "REG E10" | "E10 UNL" | "UNLD E10" | "PREM E10" | "REGULAR E10" | "E-10 REGULAR" | "E10-9-10" | "E10 MID" | "E10 PREM" | "E10 REG" | "UNLEAD E10" | "UNLD10%":
                        fuel_types_matched.append(Fuel.E10)
                    case "E15" | "E-15":
                        fuel_types_matched.append(Fuel.E15)
                    case "E20" | "E-20":
                        fuel_types_matched.append(Fuel.E20)
                    case "E30" | "E-30":
                        fuel_types_matched.append(Fuel.E30)
                    case "E-85" | "E85" | "E 85" | "E-85 ETHANOL":
                        fuel_types_matched.append(Fuel.E85)
                    case "KERO" | "KERSN" | "KEROSENE" | "KERSN/BT" | "KERS" | "KERO1" | "KEROSINE":
                        fuel_types_matched.append(Fuel.KEROSENE)
                    case "METH":
                        fuel_types_matched.append(Fuel.METHANOL)
                    case "DEF" | "DIESEL EXHAUST FLUID" | "DEF FLUID":
                        fuel_types_matched.append(Fuel.ADBLUE)
                    case _:
                        self.logger.warning(f"Fuel type '{fuel_type}' is not recognised or is ambiguous.")
            for fuel_type in fuel_types_matched:
                apply_yes_no(fuel_type, item, True)
            yield item
