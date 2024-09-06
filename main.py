import requests, json, dateutil, datetime

pretty = False


# https://www.legis.iowa.gov/docs/code/719.1.pdf
# https://www.info.iastate.edu/

class Charge:
    def decodeBondStatus(status: str) -> int:
        return 0
    def __init__(self, charge_json: dict[str]):
        self.info = {}
        self.info["law"] = charge_json["Name"]
        self.info["bond"] = charge_json["BondAmount"]
        self.info["bondStatus"] = Charge.decodeBondStatus(charge_json["BondStatus"])
        self.info["des"] = str.capitalize(charge_json["Description"])
        self.info["date"] = datetime.datetime.fromisoformat(charge_json["Date"]).replace(tzinfo=dateutil.tz.gettz("US/Central")).isoformat()

    def toJSON(self):
        return json.dumps(self.info)
    def toDict(self):
        return self.info

class Inmate:
    def parseHeight(height: str) -> int:
        return (int(height[0]) * 12) + int(height[3:5])
    
    def parseCharges(charge_json: list[any]) -> list[dict]:
        return [Charge(charge).toDict() for charge in charge_json]
        
    def __init__(self, charge_json: dict[any]):
        self.info = {}
        self.info["first"] = str.capitalize(charge_json["FirstName"])
        self.info["last"] = str.capitalize(charge_json["LastName"])
        self.info["middle"] = str.capitalize(charge_json["MiddleName"])
        self.info["race"] = str.capitalize(charge_json["Race"])
        self.info["male"] = charge_json["Sex"] == "MALE"
        self.info["charges"] = Inmate.parseCharges(charge_json["Charges"])
        self.info["height"] = Inmate.parseHeight(charge_json["Height"])
        self.info["pchar"] = 0
        self.info["img"] = "https://centraliowa.policetocitizen.com/api/Inmates/Image/241/" + charge_json["ImageId"]
        # todo look through charges
        self.info["date"] = self.info["charges"][0]["date"]
        

    def toJSON(self, pretty = False):
        return json.dumps(self.info, indent=(6 if pretty else None))

    def toDict(self):
        return self.info

def main():
    res = requests.get("https://centraliowa.policetocitizen.com/Inmates/Catalog")
    cookies = res.headers.get("Set-Cookie")

    cookies = cookies.split(",")
    i = 0
    cookie_dict = {}

    header_dict = {
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referrer": "https://centraliowa.policetocitizen.com/Inmates/Catalog",
        "Priority": "u=1, i",
        "Content-Type": "application/json"
    }

    # I hate this but it works, rewrite this in C eventually
    while i < len(cookies):
        cookies[i] = cookies[i].strip()
        if cookies[i].count("expires=") and cookies[i + 1] and cookies[i + 1][1:3].isdigit():
            cookies[i] = ' '.join(cookies[i:i + 2])
            cookies.pop(i + 1)

        temp = cookies[i].split(";")[0].split("=")
        if len(temp) == 2:
            cookie_dict[temp[0]] = temp[1]
        i += 1

    header_dict["X-Xsrf-Token"] = cookie_dict["XSRF-TOKEN"]

    opts = {
        "FilterOptionsParameters": {
            "IntersectionSearch": True,
            "SearchText": "",
            "Parameters": []
        },
        "IncludeCount": True,
        "PagingOptions": {
            "SortOptions": [
            {
                "Name": "ArrestDate",
                "SortDirection": "Descending",
                "Sequence": 1
            }
            ],
            "Take": 100,
            "Skip": 0
        }
    }

    roster_json = requests.post("https://centraliowa.policetocitizen.com/api/Inmates/241", json=opts, cookies=cookie_dict, headers=header_dict).json()

    inmates: list[dict] = []

    for inmate in roster_json["Inmates"]:
        inmates.append(Inmate(inmate).toDict())

    inmate_json = {
        "inmates": inmates,
        "len": roster_json["Total"]
    }

    f = open(f"roster.{datetime.datetime.now().timestamp()}.json", "w")
    f.write(json.dumps(inmate_json, indent=(4 if pretty else None)))
    f.close()

if __name__ == "__main__":

    main()