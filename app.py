from os import system
from flask import *
from requests import get
from json import loads
from markupsafe import escape

app = Flask(__name__)

places:dict = {\
"barton": "https://mycscgo.com/api/v3/machine/info/951c9953-0c62-4c0a-b57b-e93da388bad6",
}

styling = """
<head>
    <title>Laundry Gauntlet</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Rubik:ital,wght@0,300..900;1,300..900&display=swap" rel="stylesheet">
    <style>
    body {
        font-family: "Rubik", sans-serif;
        font-optical-sizing: auto;
        font-weight: 400;
        font-style: normal;
    }
    </style>
</head>
"""

def machines(hall):
    machines = loads(get(places[hall]).text)
    return machines

@app.route("/mach/<hall>")
def machine_list(hall):
    # return machines(hall)
    dsum = machines(escape(hall))["availabilitySummary"]["dryers"]
    wsum = machines(escape(hall))["availabilitySummary"]["washers"]
    mech = machines(escape(hall))["machines"]
    outstr = styling + f"<div>Machines Available in {hall.title()}:<br>&emsp;Washers:&emsp;{wsum["available"]}/{wsum["available"] + wsum["inUse"] + wsum["temporarilyUnavailable"]}<br>&emsp;Dryers:&emsp;{dsum["available"]}/{dsum["available"] + dsum["inUse"] + dsum["temporarilyUnavailable"]}</div>"
    wstr = "<div>&emsp;Washers:<br>"
    dstr = "<div>&emsp;Dryers:<br>"
    for m in sorted(mech, key=lambda x: x["stickerNumber"]):
        mstring = f"<div>&emsp;&emsp;{m["stickerNumber"]}:&emsp;{(m["mode"] == "pressStart" or m["available"] == True) * "Available"}{(m["timeRemaining"] > 0 and m["notAvailableReason"] == "in-use") * f"In Use, {m["timeRemaining"]} min left"}{(m["mode"] == "unknown") * "<i>???</i>"}</div>"
        if (m["type"] == "washer"):
            wstr += mstring
        if (m["type"] == "dryer"):
            dstr += mstring
    wstr += "</div>"
    dstr += "</div>"
    outstr += wstr + dstr
    return outstr

@app.route("/mach/<hall>/<mach>")
def get_mach(mach, hall):
    mech = machines(escape(hall))["machines"]
    mach = int(escape(mach))
    md = dict()
    for m in mech:
        md[m["stickerNumber"]] = m
    if mach in md.keys():
        return md[mach]
    else: return styling + "Machine Not Found"

@app.route("/halls")
def get_halls():
    return styling + "Registered halls: " + ", ".join(places.keys())

if __name__ == "__main__": # guard
    system("flask run")