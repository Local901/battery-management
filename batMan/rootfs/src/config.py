from datetime import datetime, timezone, timedelta
from dynaconf import Dynaconf
import requests
import os
from enum import Enum
from collections.abc import Callable
from typing import Dict
from schedule import Action

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

def _getValue(entityId: str | None, map: Callable[[str], any], fallback: Callable[[], any]) -> any:
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

    def getSchedule(self) -> Dict[str, Action]:
        """ Get list of time stamped actions. """
        dict: Dict[str, str] = self._settings["schedule"]
        schedule = {}
        for key in sorted(dict.keys()):
            value = dict.get(key).strip()
            if value.startswith("c"):
                [action, power] = value.split(" ")
                power = int(power)
                schedule[key] = Action(power)
            elif value.startswith("d"):
                [action, power] = value.split(" ")
                power = int(power)
                schedule[key] = Action(-power)
            else:
                schedule[key] = Action(0)

        return schedule
    
    def getIsScheduleLoop(self) -> bool:
        """ Get the flag for if the schedule should loop back to day 0 after day 1. """
        return bool(self._settings["loopSchedule"])

    def getCurrentTime(self) -> datetime:
        return datetime.now(
            timezone(
                timedelta(hours=int(self._settings["timezone"]))
            )
        )

config = Config()
