import requests
import configparser
import xml.etree.ElementTree as ET
import json
from crypto import encrypt
from gCalendar import CalendarHandler


def getTimetable(id: str, passw: str):
    REQURL = "https://campusapps.itsc.cuhk.edu.hk/store/CLASSSCHD/STT.asmx/GetTimeTable"
    HEADER = {"Content-Type": "application/x-www-form-urlencoded"}
    PARAMS = {
        "asP1": encrypt(id),
        "asP2": encrypt(passw),
        "asP3": "hk.edu.cuhk.ClassTT",
    }
    try:
        response = requests.request("POST", REQURL, data=PARAMS, headers=HEADER)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    print("*" * 41)
    print(f"{" CUHK Timetable to Google Calendar ":*^41}")
    print("*" * 41)
    print()
    config = configparser.ConfigParser()
    if len(config.read("config.ini")) == 0:
        with open("config.ini", "w") as f:
            config["DEFAULT"] = {"id": "1155123456", "password": "abcd1234"}
        print(
            "Please fill in the config.ini file with your details and run again\nexiting..."
        )
        exit()

    print("Getting timetable...\n")
    res = getTimetable(config["DEFAULT"]["id"], config["DEFAULT"]["password"])
    # with open("timetable.xml", "w") as f:
    #     f.write(res)
    # with open("timetable.xml", "r") as f:
    #     res = f.read()
    if not res:
        print("Failed to get timetable.")
        exit()

    timetable = json.loads(ET.fromstring(res).text or "[]")
    if timetable == []:
        print("No timetable found. Poissibly wrong id or password.")
        exit()

    calendarHandler = CalendarHandler()
    if not calendarHandler.init():
        print("Failed to authenticate Google Calendar.")
        exit()

    # filter timetable by term
    terms = list({x["STRM_DESCR"]: 0 for x in timetable}.keys())
    for i, term in enumerate(terms):
        print(f"Term {i}: {term}")
    while True:
        term_nums = input(
            "Please choose term(s) to insert eg, 0 3 2 15 (default=last entry): "
        ).split()
        if not term_nums:
            term_nums = [len(terms) - 1]
        else:
            term_nums = [int(x) for x in term_nums if x.isdigit()]
        terms_final = [terms[i] for i in term_nums if 0 <= i < len(terms)]
        if terms_final:
            break
        print("No valid terms selected. Please try again.")
    timetable = [x for x in timetable if x["STRM_DESCR"] in terms_final]

    calendarName = input(
        "Please enter the name of the calendar to create (default=CUHK TT): "
    )

    useHtml = input("Use HTML descriptions? (y/n, default=y): ").lower() != "n"

    print("\nCreating calendar...")
    if not calendarHandler.createCalendar(calendarName):
        print("Failed to create calendar.")
        exit()

    print("Inserting entries...")
    for i, entry in enumerate(timetable):
        if (
            entry["MEETING_TIME_START"].strip() == ""
            or entry["MEETING_TIME_END"].strip() == ""
        ):  # classes without meetings
            # (is it possible to have classes that
            #       have their days set but not the time?)
            continue
        if not calendarHandler.insert(entry, useHtml):
            print(f"Failed to insert event")
            exit()
        else:
            lenlen = len(str(len(timetable)))
            print(f"Done: {i+1:>{lenlen}}/{len(timetable)}")

    print("\nTask completed.")
