from os import system
from markupsafe import escape
import pickle, time
from datetime import datetime
from flask import *
from gaunt_data import *
from gaunt_ifaces import *

app = Flask(__name__)

styling = """
<head>
    <meta http-equiv="refresh" content="5">
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

data = dict() # time keys, [hall list] vals

@app.route("/mach")
def all_halls():
    outstr = styling + ""
    for h in halls.keys():
        outstr += machine_list(h)
    return outstr

@app.route("/save")
def save_all_halls():
    data[time.time()] = [Hall(h, [Mach(m["stickerNumber"], m["type"], m["doorClosed"], m["mode"], m["available"], m["notAvailableReason"], m["timeRemaining"]) for m in machines(h)["machines"]]) for h in halls.keys()]
    save_data()
    return styling + "data saved!"

@app.route("/mach/<hall>")
def machine_list(hall):
    dsum = machines(escape(hall))["availabilitySummary"]["dryers"]
    wsum = machines(escape(hall))["availabilitySummary"]["washers"]
    mech = machines(escape(hall))["machines"]
    outstr = styling + f"<div>Machines Available in {hall.title()}:<br>"
    wstr = f'<br><div>&emsp;Washers:&emsp;({wsum["available"]}/{wsum["available"] + wsum["inUse"] + wsum["temporarilyUnavailable"]})</div>'
    dstr = f'<br><div>&emsp;Dryers:&emsp;({dsum["available"]}/{dsum["available"] + dsum["inUse"] + dsum["temporarilyUnavailable"]})</div>'
    for m in sorted(mech, key=lambda x: x["stickerNumber"]):
        mstring = f'''<div>&emsp;&emsp;{m["stickerNumber"]}:&emsp;{((m["mode"] != "running" or m["available"] == True) and m["mode"] != "unknown") * "Available"}{(m["timeRemaining"] > 0) * f'In Use, {m["timeRemaining"]} min left'}{(m["mode"] == "unknown") * "[Unknown State]"}{(m["notAvailableReason"] == "offline") * " [Offline]"}</div>'''
        if (m["type"] == "washer"):
            wstr += mstring
        if (m["type"] == "dryer"):
            dstr += mstring
    wstr += "</div>"
    dstr += "</div>"
    outstr += wstr + dstr + "<br>"
    return outstr

@app.route("/mach/<hall>/<mach>")
def get_mach_caller(hall, mach):
    return get_mach(escape(hall), escape(mach))

@app.route("/halls")
def get_halls():
    return styling + "Registered halls: " + ", ".join(halls.keys())

def load_data():
    global data
    print("loading data...")
    try:
        with open("data.pkl", mode="rb") as f:
            data = pickle.loads(f.read())
            f.close()
    except Exception as e: print(e)

def save_data():
    global data
    print("saving data...")
    with open("data.pkl", mode="wb") as f:
        f.write(pickle.dumps(data))
        f.close()

@app.route("/view")
def view():
    load_data()
    outstr = styling + ""
    for t in data.keys():
        outstr += datetime.fromtimestamp(t).strftime("<br>%A, %B %d, %Y %I:%M:%S ")
        outstr += str([str(x) for x in data[t]])
        outstr += "<br>"
    return outstr

if __name__ == "__main__": # guard
    load_data()
    system("flask run")