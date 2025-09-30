from datetime import datetime, timezone, timedelta
from dynaconf import Dynaconf
import requests
import os
from enum import Enum
from collections.abc import Callable
from typing import Dict
from schedule import Action
import math

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
def _getHaState(entityId: str, default: str | None = None) -> str | None:
    """ Get the state of an entity.

        Returns: State of the entity. If this is not allowed or fails it will return None.
    """
    if (_supervisorToken is None):
        print("WARNING: No access token")
        return default

    if entityId is None:
        return default

    response = requests.get(
        "http://supervisor/core/api/states/" + entityId,
        headers = _headers
    )
    if response.status_code != 200:
        print("WARNING: Failed to get the state of '" + entityId + "'")
        print(response.text)
        return default
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

    _schedule: Dict[str, Dict[str, Action]] = None

    def __init__(self):
        pass

    def _parseScheduleAction(self, planning: str, defaultAction: Action, defaultMcp: int | None) -> Dict[str, any]:
        result = {
            "action": defaultAction,
            "minimumChargePercentage": defaultMcp
        }
        split = planning.strip().split()
        index = 0
        while index < len(split):
            try:
                match split[index].lower():
                    case "c": # charge with i + 1
                        result["action"] = Action(int(split[index + 1]))
                        index += 1
                    case "d": # discharge with i + 1
                        result["action"] = Action(-int(split[index + 1]))
                        index += 1
                    case "mcp":
                        result["minimumChargePercentage"] = max(
                            0,
                            min(
                                int(split[index + 1]),
                                100
                            )
                        )
                        index += 1
            finally:
                index += 1
        return result


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

    def getMinChargePercentage(self) -> int:
        """ Minimum charge percentage to enable discharge. """
        time = self.getCurrentTime()
        key = f"h{time.hour:02}"
        minuteKey = f"m{(math.floor(time.minute / 15) * 15):02}"
        mcp = self.getSchedule().get(key).get(minuteKey).get("minimumChargePercentage", None)
        return mcp if mcp is not None else int(self._settings["minChargePercentage"])

    def getChargePercentage(self) -> int:
        """ Get current charge percentage of the battery from HA. """
        return int(_getHaState(self._settings.get("chargeState"), "50"))

    def getControlMode(self) -> type[ControlMode]:
        """ Get the control mode. Defaults to None. """
        modeValue = str(self._settings["control_mode"]).upper()
        return ControlMode[modeValue]

    def getSchedule(self) -> Dict[str, Dict[str, Dict[str, any]]]:
        """ Get list of time stamped actions. """
        if self._schedule is not None:
            return self._schedule

        dict: Dict[str, Dict[str, str]] = self._settings["schedule"]
        schedule = {}
        for key in sorted(dict.keys()):
            minuteSchedule = {}
            lastAction = {
                "action": Action(0),
                "minimumChargePercentage": None
            }
            for minuteKey in ["m00", "m15", "m30", "m45"]:
                configuredAction = dict.get(key, "").get(minuteKey, "")
                lastAction = self._parseScheduleAction(
                    configuredAction,
                    lastAction.get("action"),
                    lastAction.get("minimumChargePercentage")
                ) if configuredAction != "" else lastAction
                minuteSchedule[minuteKey] = lastAction
            schedule[key] = minuteSchedule

        self._schedule = schedule
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
