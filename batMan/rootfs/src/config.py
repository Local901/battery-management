from datetime import datetime, timezone, timedelta
from dynaconf import Dynaconf
import requests
import os
from enum import Enum
from collections.abc import Callable
from typing import Dict

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
def _getHaState(entityId: str) -> str | None:
    """ Get the state of an entity.

        Returns: State of the entity. If this is not allowed or fails it will return None.
    """
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
    return response.json()["state"]

def _getValue(entityId: str | None, map: Callable[[str], Any], fallback: Callable[[], Any]) -> Any:
    try:
        if (entityId != None):
            state = _getHaState(entityId)
            if (state != None):
                return map(state)
    finally:
        return fallback()


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
            # Add a extra action if no actions are taken in the current day.
            if day == "1" and len(schedule) == 0:
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
            elif len(schedule) == 0 and prev != "0":
                # insert a action at the current time if a action should ave been taken previously.
                schedule.append(currentTime.hour + ":" + currentTime.minute + " " + prev)

            # append next scheduled action
            schedule.append(hour + ":00 " + next)
        return self._settings["schedule"]

    def getCurrentTime(self) -> datetime:
        return datetime.now(
            timezone(
                timedelta(hours=int(self._settings["timezone"]))
            )
        )

config = Config()
