# Run in production: flask --app --host=0.0.0.0 main run
# Run in debugging: flask --app main run

from ast import arg
from distutils.log import debug
from itertools import dropwhile
from flask import Flask, render_template, redirect, url_for
import threading, os
import time, datetime

app = Flask(__name__)
app.config["DEBUG"] = False

# Flask app
@app.route("/")
def index():
    return redirect(url_for("monitor"))

@app.route("/solar-monitor", methods=["GET"])
def monitor():
    curr_vol = voltage
    curr_amp = dropdown_voltage
    curr_wat = voltage * dropdown_voltage
    curr_effwat = voltage * dropdown_voltage * 0.7
    pk_wat = 230

    return render_template("monitor.html", curr_amp=curr_amp, curr_vol=curr_vol, curr_wat=curr_wat, curr_effwat= curr_effwat, pk_wat=pk_wat)

def scrape_Hardware():
    global dropdown_voltage
    while(thread_frontend.is_alive()):
        dropdown_voltage += 1
        time.sleep(2)

if __name__ == "__main__":
    # Hardware parameter
    dropdown_voltage = 1.25
    voltage = 33

    thread_frontend = threading.Thread(target=app.run, args=(), daemon=False)
    thread_scraping = threading.Thread(target=scrape_Hardware, args=(), daemon=False)

    try:
        thread_frontend.start()
        thread_scraping.start()

        thread_frontend.join()
        thread_scraping.join()
    except:
        print("Interrupted.")
    