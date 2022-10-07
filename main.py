# Run in production: flask --app --host=0.0.0.0 main run
# Run in debugging: flask --app main run

from asyncore import read
from random import randint
from flask import Flask, render_template, redirect, url_for
import threading
import time, csv
from datetime import datetime

app = Flask(__name__)
app.config["DEBUG"] = False

def log(applicationString):
    with open('data/log', 'a', newline='') as note:
        datestring = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        note.write(f"[{datestring}]  {applicationString}\n")
        note.close()

# Flask app
@app.route("/")
def index():
    return redirect(url_for("monitor"))

@app.route("/solar-monitor", methods=["GET"])
def monitor():
    curr_wat = curr_vol * curr_amp
    curr_effwat = curr_wat * 0.7
    log("HTTP Request for .../solar-monitor")

    return render_template("monitor.html", 
        curr_amp=curr_amp, curr_vol=curr_vol, curr_wat=curr_wat, curr_effwat= curr_effwat, 
        pk_wat=pk_wat, price_wat=price_wat, total_wat=total_wat, tod_wat=wat_today,
        lit_wat=lit_wat, chart_dic=chart_dic)

def scrape_Hardware():
    counter = 0

    # Clear latest.csv
    f = open('data/latest.csv', "w+")
    f.close()

    while(True): # thread_frontend.is_alive()
        # Get voltage reading of analog to digital converter
        dropdown_voltage = 5.14
        module_voltage = 30

        wat = dropdown_voltage * module_voltage

        # Setting today peak wattage
        global pk_wat
        if(wat > pk_wat):
            pk_wat = wat

        # Writing data to Daily log
        data = [datetime.now().strftime("%H:%M:%S"), module_voltage, dropdown_voltage, wat, wat * 0.7]
        log(f"Writing to daily log: {wat} W")
        with open('data/latest.csv', 'a+', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(data)
            file.close()

        # Writing data 
        global wat_today
        wat_today += (wat * refreshing_interval) / 3600000
        if(counter >= 3600 / refreshing_interval):
            wat_h = wat_today - wat_h_old

            # Adding to all time sum
            val = 0

            with open('data/sum-all.txt', 'r', newline='') as file:
                val = (float)(file.readline())
                log(f"Reading from all-time sum: {val} kWh")
                file.close()

            with open('data/sum-all.txt', 'w', newline='') as file:
                log(f"Adding to all-time sum: {wat_h} W")
                
                global total_wat
                total_wat = val + wat_h
                file.write(total_wat)
                file.close()

            counter = 0
            data = [datetime.now().strftime("%m/%d/%Y"), (wat * refreshing_interval) / 3600000]
            wat_h_old = wat_today

            # Write to all-time log
            with open('data/all-time.csv', 'a+', newline='') as file:
                log(f"Adding to all-time sum: {wat_h} W")
                writer = csv.writer(file)
                writer.writerow(data)
                file.close()
            
            # Setup diagram dictionary
            global chart_dic
            chart_dic.clear()
            log("Setting up Diagram dictionary.")

            for i in range(24):
                if(i < 24 - len(wat_log)):
                    chart_dic.append(0)
                elif(len(wat_log) > 0):
                    ind = i - (24 - len(wat_log))
                    val = list(wat_log[ind])[3]
                    chart_dic.append(float(val))

        # Read data
        wat_log = {}
        with open('data/latest.csv', 'r') as file:
            log("Reading from latest.csv.")
            reader = csv.DictReader(file)
            line = 0
            for row in reader:
                wat_log[line] = row
                line += 1
        
        # Calculate stats
        global curr_vol, curr_amp
        curr_vol = module_voltage
        curr_amp = dropdown_voltage

        # Rest for next scrape
        time.sleep(refreshing_interval)
        counter += 1
        log("----------------------------------------")

        # Reset daily sum by midnight
        if(datetime.now().strftime("%H:%M") == "00:00"):
            wat_today = 0
            wat_h_old = 0

            # Clear latest.csv
            f = open('data/latest.csv', "w+")
            f.close()

            log("Reseting daily sum.")
            log("Clearing daily log.")

if __name__ == "__main__":
    # Hardware parameter
    curr_vol = 30
    curr_amp = 9
    
    # Including values
    lit_wat = 350
    pk_wat = 0
    price_wat = 0
    total_wat = 0

    refreshing_interval = 5
    wat_today = 0
    wat_h_old = 0
    chart_dic = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]


    thread_frontend = threading.Thread(target=app.run, args=(), daemon=False)
    thread_scraping = threading.Thread(target=scrape_Hardware, args=(), daemon=False)

    # Clear log
    f = open('data/log.', "w+")
    f.close()
    log("##### Starting application. #####")

    #scrape_Hardware()
    #app.run(debug=True)

    try:
        #app.run(debug=True)
        thread_frontend.start()
        thread_scraping.start()

        thread_frontend.join()
        thread_scraping.join()
    except:
        print("Interrupted.")

    log("Closing application.")

    