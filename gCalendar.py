# type: ignore
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError
import random

# changing this will require re-authentication (delete token.json)
SCOPES = ["https://www.googleapis.com/auth/calendar.app.created"]

# TODO: https://developers.google.com/calendar/api/v3/reference/events
# colorId: make sure same classes have same color; decide using CRSE_ID
# description: can contain html; STRM_DESCR, DESCR, CATALOG_NBR, FDESCR, INSTRUCTORS, COMDESC CLASS_SECTION
#              p.s. html causes issues sometimes. (maybe make it optional?)
# end.dateTime: START_DT + MEETING_TIME_END
# end.timeZone: "Asia/Hong_Kong"
# location: LAT LNG
# recurrence[]:  END_DT, MON, TUES, WED, THURS, FRI, SAT, SUN
# start.dateTime: START_DT + MEETING_TIME_START
# start.timeZone: "Asia/Hong_Kong"
# summary: SUBJECT CATALOG_NBR FACILITY_ID SSR_COMPONENT

# unused props: K STRM CLASS_MTG_NBR BLDG_CD, CLASS_NBR SSR_COMPONENT1


def getColor():
    random.seed(datetime.datetime.now().timestamp())
    x = {}
    cnt = 0
    ids = list(range(11))
    random.shuffle(ids)
    CRSE_ID = -1
    x[CRSE_ID] = None

    while True:
        event_record = yield x[CRSE_ID]
        CRSE_ID = event_record["CRSE_ID"]
        if not CRSE_ID in x:
            x[CRSE_ID] = ids[cnt] + 1
            cnt += 1
            cnt %= 11


def getDescr(event_record: dict, html):
    HTMLFORMAT = f"""<h2>{event_record["DESCR"]} ({event_record["CATALOG_NBR"]})
{event_record["STRM_DESCR"]}</h2><p><strong>Location</strong>: {event_record["FDESCR"]}
<strong>Instructor(s)</strong>: {event_record["INSTRUCTORS"]}
<strong>Component</strong>: {event_record["COMDESC"]}
<strong>Section</strong>: {event_record["CLASS_SECTION"]}</p>"""

    PLAINFORMAT = f"""{event_record["DESCR"]} ({event_record["CATALOG_NBR"]})
{event_record["STRM_DESCR"]}
Location: {event_record["FDESCR"]}
Instructor(s): {event_record["INSTRUCTORS"]}
Component: {event_record["COMDESC"]}
Section: {event_record["CLASS_SECTION"]}"""

    return HTMLFORMAT if html else PLAINFORMAT


def getEndDateTime(event_record: dict):
    # START_DT=20240416, MEETING_TIME_END=14:30
    endstr = event_record["START_DT"] + event_record["MEETING_TIME_END"]
    return datetime.datetime.strptime(endstr, "%Y%m%d%H:%M").isoformat()


def getRecurrence(event_record: dict):
    days = ["MON", "TUES", "WED", "THURS", "FRI", "SAT", "SUN"]
    byday = []
    for day in days:
        if event_record[day] == "Y":
            byday.append(day[:2])

    return [
        "RRULE:FREQ=WEEKLY;BYDAY="
        + ",".join(byday)
        + ";UNTIL="
        + event_record["END_DT"]
    ]


def getStartDateTime(event_record: dict):
    # START_DT=20240416, MEETING_TIME_START=13:30
    startstr = event_record["START_DT"] + event_record["MEETING_TIME_START"]
    return datetime.datetime.strptime(startstr, "%Y%m%d%H:%M").isoformat()


def getSummary(event_record: dict):
    return f'{event_record["SUBJECT"]}{event_record["CATALOG_NBR"]} {event_record["SSR_COMPONENT"]} {event_record["FACILITY_ID"]}'


def getEventObject(event_record: dict, colorId, useHtml):
    return {
        "colorId": colorId,
        "description": getDescr(event_record, useHtml),
        "end": {"dateTime": getEndDateTime(event_record), "timeZone": "Asia/Hong_Kong"},
        "location": f'{event_record["LAT"]} {event_record["LNG"]}',  # for some reason lng already has a space
        "recurrence": getRecurrence(event_record),
        "start": {
            "dateTime": getStartDateTime(event_record),
            "timeZone": "Asia/Hong_Kong",
        },
        "summary": getSummary(event_record),
    }


def authGCalendar():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    try:
        return build("calendar", "v3", credentials=creds)
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None


def insertEvent(
    service: Resource,
    calendarId: str,
    event_record: dict[str, str],
    colorId: str,
    useHtml: bool,
):
    if not colorId:
        colorId = random.randint(1, 11)
    try:
        service.events().insert(
            calendarId=calendarId, body=getEventObject(event_record, colorId, useHtml)
        ).execute()
        return True
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None


def createCalendar(service: Resource, name: str) -> str | None:
    try:
        res = service.calendars().insert(body={"summary": name}).execute()
        return res["id"]
    except HttpError as e:
        print(f"An error occurred: {e}")
        return None


class CalendarHandler:
    def __init__(self):
        self._service = None
        self._calendarId = None
        self._colorGen = getColor()
        next(self._colorGen)

    def init(self):
        self._service = authGCalendar()
        if not self._service:
            return False
        return True

    def createCalendar(self, name: str):
        if not self._service:
            return False
        if name == "":
            name = "CUHK TT"
        self._calendarId = createCalendar(self._service, name)
        if not self._calendarId:
            return False
        return True

    def insert(self, event_record: dict[str, str], useHtml: bool):
        if not self._calendarId:
            return False
        return (
            insertEvent(
                self._service,
                self._calendarId,
                event_record,
                self._colorGen.send(event_record),
                useHtml,
            )
            is not None
        )
