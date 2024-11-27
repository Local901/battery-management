from customTime import Time, currentTime

class TimeFrame():
    time = currentTime()
    action = "none"
    power = 0

    def __init__(self, time: Time, action: str, power = 0):
        self.time = time
        self.action = action
        self.power = power
    
def parseTimeFrame(value: str) -> TimeFrame:
    """
    Parse a time frame string.

    **Format**: '<time: hh:mm> <action: 0|c|d> [<power: number>]'

    **Example**: '15:10 c 4000'
    """
    splitValue = [v for v in value.split() if v != '']

    if 1 < len(splitValue) < 4:
        raise Exception(f"Expected two or three parts. \nExpected: '<time: hh:mm> <action: 0|c|d> [<power: number>]'\nRecieved: {value}")
    
    if len(splitValue) >= 2:
        if not str.__contains__(splitValue[0], ":"):
            raise Exception(f"Expected first part to be a time but found: '{splitValue[0]}'")
        
        splitTime = splitValue[0].split(':')
        splitValue[0] = Time(int(splitTime[0]), int(splitTime[1]))

        splitValue[1] = splitValue[1].lower()

    if len(splitValue) == 3:
        splitValue[2] = int(splitValue[2])
    
    return TimeFrame(*splitValue)
