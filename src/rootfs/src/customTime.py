from datetime import datetime, timezone

class Time():
    hour = 0
    minutes = 0

    def __init__(self, hour: int, minutes: int):
        self.hour = hour
        self.minutes = minutes
        pass

    def __str__(self) -> str:
        return f"{self.hour}:{self.minutes}"

    def isBeforeNow(self, butAfter = None) -> bool:
        """
        Check if the current time is past the time set in this object.
        """

        # Return False if the time false before butAfter and it isn't the next day yet.
        if (butAfter is not None) and self.before(butAfter) and Time.isBeforeNow(butAfter):
            return False

        currentTime = datetime.now()
        if self.hour < currentTime.hour:
            return True
        elif self.hour == currentTime.hour and self.minutes <= currentTime.minute:
            return True
        return False
    
    def before(self, other) -> bool:
        if self.hour < other.hour:
            return True
        elif self.hour == other.hour and self.minutes < other.minutes:
            return True
        return False

def currentTime() -> Time:
    currentTime = datetime.now()
    return Time(currentTime.hour, currentTime.minute)