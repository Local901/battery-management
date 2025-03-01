from datetime import datetime, timezone, timedelta
from typing import Any
from dynaconf import Dynaconf
import requests
import os
from enum import Enum
from typing import Dict
from hourPrices import HourPriceList, HourPrice

class ControlMode(Enum):
    NONE = 1
    CHARGE = 2
    DISCHARGE = 3
    SCHEDULE = 4


_supervisorToken = os.getenv("SUPERVISOR_TOKEN")
_headers = {
    "content-type": "application/json",
}
if (_supervisorToken != None):
    _headers["Authorization"] = "Bearer " + _supervisorToken

# https://developers.home-assistant.io/docs/api/rest/
def _getHaStateObject(entityId: str) -> Any | None:
    if (entityId is None):
        print("WARNING: Entity id is undefined.")
        return None
    if (_supervisorToken is None):
        print("WARNING: No access token")
        return None

    response = requests.get(
        "http://supervisor/core/api/states/" + entityId,
        headers = _headers
    )
    if response.status_code != 200:
        print("WARNING: Failed to get the state of '" + entityId + "'")
        print(response.text)
        return None
    return response.json()

def _getHaState(entityId: str) -> str | None:
    """ Get the state of an entity.

        Returns: State of the entity. If this is not allowed or fails it will return None.
    """
    state = _getHaStateObject(entityId)
    if (state == None):
        return None
    return state["state"]

def _getHaAttributes(entityId: str) -> Any | None:
    state = _getHaStateObject(entityId)
    if (state == None):
        return None
    return state["attributes"]


class Config:
    _settings = Dynaconf(
        settings_files=["/data/options.json"],
    )

    def __init__(self):
        pass

    def getHost(self) -> str:
        return self._settings["host"]

    def getPort(self) -> int:
        return int(self._settings["port"])

    def getDelay(self) -> int:
        """ Delay in seconds between reconnection attempts. """
        return int(self._settings["delay"])

    def getTimeout(self) -> int:
        """ Timeout in seconds between requests. """
        return int(self._settings["timeout"])

    def getControlMode(self) -> type[ControlMode]:
        """ Get the control mode. Defaults to None. """
        modeValue = str(self._settings["control_mode"]).upper()
        return ControlMode[modeValue]

    def getSchedule(self) -> list[str]:
        """ Get inputted schedule. syntax '<time 00:00> <action 0|c|d> [power int]' """
        dict: Dict[str, str] = self._settings["schedule"]
        currentTime = self.getCurrentTime()
        schedule = []
        prev = "0"
        for key in sorted(dict.keys()):
            day = key[1:2]
            hour = int(key[3:])
            # Add a extra action before the next day to prevent leaping.
            if day == "1":
                schedule.append("23:50 " + prev)

            value = dict.get(key)

            # change the next value when a valid action has been set.
            if value[:1] == "c" or value[:1] == "d" or value == "0":
                # skip when action didn't change
                if value == prev:
                    continue
                prev = value
            else:
                continue

            # Skip hours that are already passed
            if "0" != day and currentTime.hour >= hour:
                continue
            elif len(schedule) <=1 and currentTime.hour >= hour:
                # set first action at the current time if a action should have been taken previously.
                schedule = [str(currentTime.hour) + ":" + str(currentTime.minute) + " " + prev]
                continue

            # append next scheduled action
            schedule.append(str(hour) + ":00 " + prev)
        
        return schedule

    def getCurrentTime(self) -> datetime:
        return datetime.now(
            timezone(
                timedelta(hours=int(self._settings["timezone"]))
            )
        )
    
    def getHourPriceList(self) -> HourPriceList | None:
        attributes = _getHaAttributes(self._settings["device_price_list"])
        if (attributes is None): return None

        prices = attributes["prices"]
        if (prices is None): return None

        priceList = HourPriceList()

        for price in prices:
            time = datetime.strptime(price["time"], "%Y-%m-%d %H:%M:%S%:z")
            priceList.addPrice(HourPrice(time, price["price"]))

        return priceList


config = Config()
