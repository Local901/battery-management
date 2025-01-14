from datetime import datetime
from dynaconf import Dynaconf
from schedule import parseTimeFrame, TimeFrame

class ControlMode(Enum):
    NONE = 1
    CHARGE = 2
    DISCHARGE = 3
    SCHEDULE = 4

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
    
    def getSchedule(self) -> list[TimeFrame]:
        """ Get parsed schedule frames.
        Raises: Exception when schedule is miss-configured.
        """
        frames: list[TimeFrame] = []
        for value in self._settings["schedule"]:
            frames.append(parseTimeFrame(value))

        return frames
    
    def getCurrentTime(self) -> datetime:
        return datetime.now()

config = Config()
