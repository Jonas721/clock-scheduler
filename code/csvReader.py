import csv
import PIController
from datetime import datetime
import time
import threading
from flask import Flask, redirect, render_template, request, url_for

app = Flask(__name__)

# switch this to the test file name for more convenient testing without messing up the schedule
scheduleFileName = "schedule.csv"

PIController.setupGPIO()


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        print("request.files is: " + str(request.files))
        file = request.files.getlist('fileInput')[0]
        print("file name is: " + file.filename)

        """
        This is leftover from when I wasn't really clear on what to do.
        I left it in here in case I ever need to modify the code to allow uploading
        of custom csv files, but I think just having one hardcoded in is totally fine for now.
        """
        # try:
        #     content = file.read()
        #     text_content = content.decode('utf-8', errors='ignore')  # Decode the raw filestream
        #     #print(text_content) 
        #     # FYI rn the csvReader function is hardcoded to read from the schedule.csv file; not this uploaded one
        #     readCsv()
        # except Exception as e:
        #     print("Error reading file: " +  str(e))
        #     return "Error processing file", 400

    return render_template('index.html')


def readCsv():
    """
    Reads the schedule from the CSV file and organizes it into a dictionary structure for easy access.
    Returns:
    dict: A dictionary containing the schedule information organized by zone and day
    """
    scheduleDict = {}
    newZone = False
    currentZoneName = ""
    weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Holiday Break"]
    weekdaysIndex = 0

    with open(scheduleFileName, newline="") as scheduleFile:
        reader = csv.reader(scheduleFile)
        for row in reader:
            #print(row)
            if (newZone == True):
                newZone = False
                weekdaysIndex = 0
                currentZoneName = row[0]
                scheduleDict[currentZoneName] = {} 
            elif (row[0].startswith("#")):
                newZone = True
            else:
                currentDay = weekdays[weekdaysIndex]
                # have to trim empty slots from row before appending to dict
                emptySlots = row.count("")
                for emptySlot in range(emptySlots):
                    try:
                        row.remove("")
                    except ValueError:
                        pass
                scheduleDict[currentZoneName][currentDay] = row
                weekdaysIndex += 1
    return scheduleDict
    # resulting dictionary structure is zone (dict): day (dict): times (list)

def removeTimeFromCSV(targetZone, targetDay, targetTime):
    csvObj = readCsv()
    csvObj[targetZone][targetDay].remove(targetTime)
    rewriteCSVFile(csvObj)

def addTimeToCSV(targetZone, targetDay, targetTime):
    csvObj = readCsv()
    csvObj[targetZone][targetDay].append(targetTime)
    csvObj[targetZone][targetDay].sort(key=lambda t: datetime.strptime(t, "%H:%M").time())
    rewriteCSVFile(csvObj)

def toggleHolidayBreakInCSV(targetZone):
    csvObj = readCsv()
    csvObj[targetZone]["Holiday Break"][0] = "true" if csvObj[targetZone][ "Holiday Break"][0] == "false" else "false"
    rewriteCSVFile(csvObj)

def rewriteCSVFile(csvObj):
    """
    rewrites the csv file based on the provided csvObj dictionary; 
    this is used to update the schedule after adding/removing times or toggling holiday break 
    Parameters:
    csvObj (dict): The dictionary containing the updated schedule
    """
    zoneNo = 1
    with open(scheduleFileName, "w") as outputFile:
        for zone in csvObj:
            outputFile.write("# Zone " + str(zoneNo) + "\n")
            zoneNo += 1
            outputFile.write(str(zone) + "\n")
            for day in csvObj[zone]:
                for i in range(23):
                    if (i < len(csvObj[zone][day])):
                        time = csvObj[zone][day][i]
                        outputFile.write(time)
                    if (day != "Holiday Break"):
                        outputFile.write(",")
                # just making sure not to add an extra newline at the end of the file
                # (I dont really understand this logic but I actually just used Demorgan's law irl to get it!)
                if ((zoneNo != 5) or (day != "Holiday Break")):
                    outputFile.write("\n")

@app.route('/view')
def view():
    currentZone = request.args.get('zone', 'High School')
    return render_template('CRUDtimes.html', zone=currentZone, times=readCsv(), showAddTimePromptFor="")

@app.post("/delete-time")
def deleteTime():
    zone = request.form["zone"]
    day = request.form["day"]
    time = request.form["time"]

    removeTimeFromCSV(zone, day, time)
    return redirect(url_for("view", zone=zone))

@app.post("/prompt-add-time")
def promptAddTime():
    zone = request.form["zone"]
    day = request.form["day"]
    return redirect(url_for("view", zone=zone, showAddTimePromptFor=day))

@app.post("/add-time")
def addTime():
    zone = request.form["zone"]
    day = request.form["day"]
    time = request.form["time"]
    
    addTimeToCSV(zone, day, time)
    return redirect(url_for("view", zone=zone))

@app.post("/toggle-holiday-break")
def toggleHolidayBreak():
    zone = request.form["zone"]
    toggleHolidayBreakInCSV(zone)
    return redirect(url_for("view", zone=zone))


def triggerAlarm(zone):
    """
    triggers the alarm for the specified zone by activating the corresponding relay;
    wrapper function for PIController.soundAlarm()
    Parameters:
    zone (str): The zone for which to trigger the alarm (e.g., "High School", "Gym", "Cafeteria", "Undetermined")
    """
    print("ALARM TRIGGERED FOR " + zone + " at " + datetime.now().strftime("%H:%M:%S"))
    PIController.soundAlarm(zone)

def run_scheduler():
    """
    continually checks the current time against the schedule and triggers 
    the alarm when there is a match
    """
    WEEKDAY_KEY = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday"}

    while True:
        schedule = readCsv()
        now = datetime.now().strftime("%H:%M")
        weekday_int = datetime.now().weekday()   # 0–6
        weekday = WEEKDAY_KEY.get(weekday_int)   # becomes a string now
        print("Current time: " + now + ", Weekday: " + str(weekday))

        if weekday is not None:  # ignore weekends
            for zone in schedule:
                if now in schedule[zone][weekday]:
                    triggerAlarm(zone)

        time.sleep(60)  # check in 60 second intervals


if __name__ == '__main__':
    try:
        # start the constant time checker in a separate thread so that it doesnt block the flask app from running
        thread = threading.Thread(target=run_scheduler)
        thread.daemon = True
        thread.start()

        app.run(host="0.0.0.0", port=5000)
    finally:
        PIController.cleanupGPIO()  # ensure GPIO cleanup on exit
