# This script is basically an interface between the main logic and the physical raspberry pi
# allowing for easier testing on non-linux systems and convenient remapping of physical components

import time

# length of time to keep alarms on in seconds
timerLength = 5 # change as needed

GPIO = None

def setupGPIO():
    """ sets up relays for the alarms by configuring the GPIO pins belonging to each zone"""
    global GPIO

    # safety measure to enable testing on non-linux systems where the GPIO module is unavailable
    try:
        import RPi.GPIO as rpi_gpio
        GPIO = rpi_gpio
    except (ImportError, RuntimeError):
        GPIO = None
        print("WARNING: RPi.GPIO module not found. Hardware functions will be disabled.")

    if GPIO is None:
        return

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(17, GPIO.OUT) # relay 1: high school
    GPIO.setup(27, GPIO.OUT) # relay 2: gym
    GPIO.setup(22, GPIO.OUT) # relay 3: cafeteria
    GPIO.setup(23, GPIO.OUT) # relay 4: undetermined

def soundAlarm(zone):
    """
    sounds the alarm for the specified zone by activating the corresponding relay
    Parameters:
    zone (str): The zone for which to trigger the alarm (e.g., "High School", "Gym", "Cafeteria", "Undetermined")
    """
    if GPIO is None:
        return

    if (zone == "High School"):
        GPIO.output(17, GPIO.LOW)
        time.sleep(timerLength)
        GPIO.output(17, GPIO.HIGH)
    if (zone == "Gym"):
        GPIO.output(27, GPIO.LOW)
        time.sleep(timerLength)
        GPIO.output(27, GPIO.HIGH)
    if (zone == "Cafeteria"):
        GPIO.output(22, GPIO.LOW)
        time.sleep(timerLength)
        GPIO.output(22, GPIO.HIGH)
    if (zone == "Undetermined"):
        GPIO.output(23, GPIO.LOW)
        time.sleep(timerLength)
        GPIO.output(23, GPIO.HIGH)

def cleanupGPIO():
    """
    cleans up the GPIO pins by resetting them to their default state
    """
    if GPIO is None:
        return

    GPIO.cleanup()