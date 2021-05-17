# ------------------------------------------------- #
# ------------------------------------------------- #
# ------------------------------------------------- #
# ENTER INSTAGRAM USERNAME AND PASSWORD BELOW       #
# ------------------------------------------------- #
# ENTER THE HASHTAGS YOU WISH THE BOT TO CYCLE      #
# THROUGH IN THE HASHTAGLIST ARRAY                  #
# ------------------------------------------------- #
# ADJUST THE USER VARIABLES IF DESIRED.             #
# THE VARIANCE WILL CREATE A VALUE ABOVE AND BELOW  #
# THE DESIRED AVERAGE FOR THE BOT TO CALCULATE      #
# VALUES FROM. THIS WILL MAKE IT LESS BOT LIKE      #
# AND MORE HUMAN LIKE....KIND OF.                   #
# ------------------------------------------------- #
# ------------------------------------------------- #
# IF THE BOT IS LEFT LONG ENOUGH FOR TO GO LONGER   #
# THAN A DAY, THE OPERATIONAL TIME SHOULD SHIFT     #
# EACH DAY DUE TO THE TOTAL DAY (DAY + SLEEP TIME)  #
# BEING SMALLER THAN 24 HOURS. THIS IS TO           #
# EVENTUALLY TARGET ALL TIME ZONES ACROSS THE WORLD.#
# ------------------------------------------------- #
# ------------------------------------------------- #


import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
import time
from random import randint
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
options = Options()
options.headless = True
browser = webdriver.Firefox(firefox_options=options)


# -----------------------
# ---- USER VARIABLS ----
# -----------------------

userUsername = "***USERNAME GOES HERE***"
userPassword = "***PASSWORD GOES HERE***"

# ENTER DESIRED HASHTAGS INTO HASHTAGLIST ARRAY
hashtagList = []

likesDailyAve = 700
likesDailyVariance = 0.3

likeDelayAve = 6
likeDelayVariance = 0.8

cyclesDailyAve = 80
cyclesDailyVariance = 0.2

sleepTimeAveHours = 8
sleepTimeAveVarience = 0.2

timeDelay = 3  # (seconds)
errorSleep = 30  # (seconds)


# ------------------------
# - GLOBAL/SET VARIABLES -
# ------------------------

# Time variables
dailySecondsIRL = 86400
secondsToday = 0
secondsTodayAdjusted = 0
hourlySeconds = 3600
sleepTonight = 0
cycleDelaySeconds = []

# Counter variables
likesToday = 0
likesTodayTotal = 0
likesTotal = 0
likeCounter = 0
cyclesToday = 0
cycleLikes = 0
errorsToday = 0
errorsTotal = 0

# Placeholder variables
randomTag = ''
hashtagListCycled = []


# -----------------------
# -------- PATHS --------
# -----------------------

pathLoginURL = "https://www.instagram.com/accounts/login/"
usernamePath = '/html/body/div[1]/section/main/div/div/div[1]/div/form/div/div[1]/div/label/input'
passwordPath = '/html/body/div[1]/section/main/div/div/div[1]/div/form/div/div[2]/div/label/input'
loginButtonPath = '/html/body/div[1]/section/main/div/div/div[1]/div/form/div/div[3]/button'
pictureOpenPath = '/html/body/div[1]/section/main/article/div[2]/div/div[1]/div[1]/a/div[1]/div[2]'
tagURLPath = 'https://www.instagram.com/explore/tags/'
heartPath = '/html/body/div[5]/div[2]/div/article/div[3]/section[1]/span[1]/button'
pictureNextPath = "[class=' _65Bje  coreSpriteRightPaginationArrow']"


# -----------------------
# - CALCULATED VARIABLS -
# -----------------------

likesDailyMin = round(likesDailyAve - (likesDailyAve * likesDailyVariance))
likesDailyMax = round(likesDailyAve + (likesDailyAve * likesDailyVariance))
likeDelayMin = round(likeDelayAve - (likeDelayAve * likeDelayVariance))
likeDelayMax = round(likeDelayAve + (likeDelayAve * likeDelayVariance))
cyclesDailyMin = round(cyclesDailyAve - (cyclesDailyAve * cyclesDailyVariance))
cyclesDailyMax = round(cyclesDailyAve + (cyclesDailyAve * cyclesDailyVariance))
sleepTimeAve = sleepTimeAveHours * hourlySeconds
sleepTimeMin = round(sleepTimeAve - (sleepTimeAve * sleepTimeAveVarience))
sleepTimeMax = round(sleepTimeAve + (sleepTimeAve * sleepTimeAveVarience))


# -----------------------
# --- MAIN FUNCTIONS ----
# -----------------------

# Launches browser and navigates to instagram
def launch(browser):
    print("")
    print(timeStamp(), "Launching browser")
    browser.get(pathLoginURL)
    time.sleep(timeDelay)

# Enters username/password and logs in


def login(browser):
    print(timeStamp(), "Logging in")
    browser.find_element_by_xpath(usernamePath).send_keys(userUsername)
    browser.find_element_by_xpath(passwordPath).send_keys(userPassword)
    browser.find_element_by_xpath(loginButtonPath).click()
    time.sleep(timeDelay)

# Daily cycle


def cycleDay():
    global sleepTonight
    global secondsToday
    global secondsTodayAdjusted
    global likesToday
    global cyclesToday
    global likesTodayTotal

    # Daily loop loops indefinitely. Generates randomised variables for use throughout the day
    while True:
        cycleCounter = 0
        likesTodayTotal = 0
        cycleDelaySeconds.clear()
        likesToday = randint(likesDailyMin, likesDailyMax)
        cyclesToday = randint(cyclesDailyMin, cyclesDailyMax)
        sleepTonight = randint(sleepTimeMin, sleepTimeMax)
        secondsToday = dailySecondsIRL - sleepTonight
        # Daily seconds adjusted to account for delays and other process times
        secondsTodayAdjusted = dailySecondsIRL - sleepTonight - \
            ((likeDelayAve + timeDelay) * likesToday)
        generateCycleDelaySeconds()

        print(timeStamp(), "STARTING NEW DAY")
        print(timeStamp(), "Likes today:", likesToday)
        print(timeStamp(), "Cycles today:", cyclesToday)
        print(timeStamp(), "Awake today (hours):", secondsToday//hourlySeconds)
        print("")
        print("**********************************")

        # Loops through until daily hashtag cycle count has been reached
        while cycleCounter < cyclesToday:
            cycleHashtag()
            cycleCounter += 1

            print("**********************************")
            print("")
            print(timeStamp(), "Completed cycle",
                  cycleCounter, "of", cyclesToday)
            print("")
            i = 1
            for k, v in Counter(hashtagListCycled).items():
                print(f" {k:.<22}{v:>1}")
                i += 1
            print("")
            print(timeStamp(), "Total likes today:", likesTodayTotal)
            print(timeStamp(), "Total errors today:", errorsToday)
            print(timeStamp(), "Napping for",
                  (cycleDelaySeconds[cycleCounter])//60, "minutes")
            print(timeStamp(), "Waking at " + str(datetime.now() +
                  timedelta(seconds=cycleDelaySeconds[cycleCounter])))
            print("")
            print("**********************************")

            time.sleep(cycleDelaySeconds[cycleCounter])

        print("")
        print(timeStamp(), "FINISHED DAY")
        print(timeStamp(), "Likes today:", likesTodayTotal)
        print(timeStamp(), "Likes total:", likesTotal)
        print(timeStamp(), "Errors today:", errorsToday)
        print(timeStamp(), "Total errors:", errorsTotal)
        print("")
        i = 1
        for k, v in Counter(hashtagListCycled).items():
            print(f" {k:.<22}{v:>1}")
            i += 1
        print("")
        print(timeStamp(), "Sleeping for", sleepTonight//hourlySeconds, "hours")
        print(timeStamp(), "Waking at", timeStamp()+sleepTonight)
        print("")
        print("**********************************")

        time.sleep(sleepTonight)

# Hashtag cycle function. Generates random variables for use throughout cycle


def cycleHashtag():
    global likesTodayTotal
    global likesTotal
    global hashtagListCycled
    global likeCounter
    global errorsToday
    global errorsTotal

    likeCounter = 0  # Counter for when picture is liked
    cycleLikes = likesToday // cyclesToday  # Defines how many likes per cycle
    # Picks a random tag from array
    randomTag = hashtagList[randint(0, len(hashtagList)-1)]
    hashtagListCycled.append(randomTag)  # Creates list of visited tags

    print(timeStamp(), "STARTING NEW CYCLE")
    print(timeStamp(), "Loading hashtag:", randomTag)
    print(timeStamp(), "Starting cycle of", cycleLikes, "likes")
    print("")

    # Loads hashtag URL from random hashtag generation above ^^
    browser.get(str(tagURLPath) + str(randomTag))
    time.sleep(timeDelay)

    # Clicks to open picture
    browser.find_element_by_xpath(pictureOpenPath).click()
    time.sleep(timeDelay)

    # Loop for liking pictures. Breaks out when like counter has reaches cycle likes.
    while True:

        # Try to like picture. Catches page errors in except when browser doesn't load next image properly
        try:
            # Clicks heart to like picture
            browser.find_element_by_xpath(heartPath).click()
            likeCounter += 1
            likesTodayTotal += 1
            print(timeStamp(), "Liked picture", likeCounter,
                  "(ID:", browser.current_url.split("/")[4], ")")

        # Catches any errors in clicking buttons due to page sometimes not loading correctly. Sleeps for defined time.
        except:
            errorsToday += 1
            errorsTotal += 1
            print("******************")
            print(timeStamp(), "Bot encountered an error")
            print(timeStamp(), "Error count today:", errorsToday)
            print(timeStamp(), "Error count total:", errorsTotal)
            print(timeStamp(), "Sleeping for", errorSleep,
                  "seconds and then reloading hashtag", randomTag)
            print("******************")
            time.sleep(errorSleep)

            # Loads current hashtag URL
            browser.get(str(tagURLPath) + str(randomTag))
            time.sleep(timeDelay)

            # Clicks to open picture
            browser.find_element_by_xpath(pictureOpenPath).click()
            time.sleep(timeDelay)

            # Clicks through pictures up until likeCount reached to avoid liking previously liked pictures.
            i = 0
            while i < likeCounter:
                browser.find_element_by_css_selector(pictureNextPath).click()
                print(timeStamp(), "Clicked next to return to previous position")
                i += 1
                time.sleep(timeDelay)

        # Causes cycle to break out before setting delay
        if likeCounter >= cycleLikes:
            break

        # Random time delay between liking pictures
        likeDelaySeconds = randint(likeDelayMin, likeDelayMax)
        print(timeStamp(), "Next picture in", likeDelaySeconds, "seconds")
        time.sleep(likeDelaySeconds)

        # Clicks next picture
        browser.find_element_by_css_selector(pictureNextPath).click()
        time.sleep(timeDelay)

    likesTotal += likeCounter

# Main run function. Variables are a mix of user-defined and calculated from user-defined.


def main():

    print(timeStamp(), "Starting bot...")
    print("")
    print(" *************************************************")
    print("")
    print(" DEFINED VARIABLES")
    print(" *****************")
    print("")
    print(" LIKES PER DAY")
    print(" Average:", likesDailyAve)
    print(" Variance", likesDailyVariance)
    print(" Minimum:", likesDailyMin)
    print(" Maximum:", likesDailyMax)
    print("")
    print(" LIKE DELAY")
    print(" Average:", likeDelayAve)
    print(" Variance", likeDelayVariance)
    print(" Minimum:", likeDelayMin)
    print(" Maximum:", likeDelayMax)
    print("")
    print(" CYCLES PER DAY")
    print(" Average:", cyclesDailyAve)
    print(" Variance", cyclesDailyVariance)
    print(" Minimum:", cyclesDailyMin)
    print(" Maximum:", cyclesDailyMax)
    print("")
    print(" SLEEP TIME (HOURS)")
    print(" Average:", sleepTimeAveHours)
    print(" Variance", sleepTimeAveVarience)
    print(" Minimum:", sleepTimeMin / 3200)
    print(" Maximum:", sleepTimeMax / 3200)
    print("")
    print(" DELAYS (SECONDS)")
    print(" Page load:", timeDelay)
    print(" In case of error:", errorSleep)
    print("")
    print(" *************************************************")

    launch(browser)
    login(browser)
    cycleDay()


# -----------------------
# --- MISC FUNCTIONS ----
# -----------------------

# Timestamp function for use in printing to console
def timeStamp():
    return datetime.now().strftime("(%H:%M:%S)")


# Function generates cycle delay times and populates cycleDelaySeconds array with varying integers, totalling the total work-time of the day.
def generateCycleDelaySeconds():

    newArray = []
    i1 = 0
    i2 = 0

    # CREATE ARRAY OF RANDOM INTEGERS. Append random integers into newArray using while loop.  Loop count will be length of cyclesToday.
    while i1 < cyclesToday:
        newArray.append(randint(1, 100))
        i1 += 1

    # GENERATE MULTIPLIER - Divide secondsToday by sum of newArray
    multiplier = secondsTodayAdjusted // sum(newArray)

    # CREATE ARRAY  While loop populates cycleDelaySeconds with items from newArray multiplied by multiplier
    while i2 < len(newArray):
        cycleDelaySeconds.append(newArray[i2] * multiplier)
        i2 += 1


main()
