from datetime import datetime, timezone, timedelta
from dynaconf import Dynaconf
import requests
import os
from enum import Enum

class ControlMode(Enum):
    NONE = 1
    CHARGE = 2
    DISCHARGE = 3
    SCHEDULE = 4


_supervisorToken = os.environ.get("SUPERVISOR_TOKEN")
_headers = {
    "Authorization": "Bearer " + _supervisorToken,
    "content-type": "application/json",
}

# https://developers.home-assistant.io/docs/api/rest/
def _getHaState(entityId: str) -> str | None:
    """ Get the state of an entity.

        Returns: State of the entity. If this is not allowed or fails it will return None.
    """
    if (_supervisorToken is None):
        return None
    
    response = requests.get(
        "http://supervisor/core/api/states/" + entityId,
        headers = _headers
    )
    if response.status_code != 200:
        print("WARNING: Failed to get the state of '" + entityId + "'")
        return None
    return response.json()["state"]

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
        return self._settings["schedule"]

    def getCurrentTime(self) -> datetime:
        return datetime.now(
            timezone(
                timedelta(hours=int(self._settings["timezone"]))
            )
        )

config = Config()
