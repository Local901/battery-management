from modbus import ModbusClient
from config import config, ControlMode
import time
import math

def sendToInverter(
    client: ModbusClient,
    active: bool,
    rendament: int,
):
    """
    ### Send new state to the inverter.

    **client**: The client to send modbus requests with.

    **active**: Should the inverter store energy

    **rendament**: The wanted rendament of the inverter to the battery
    """

    if (not active) or rendament == 0 or (rendament < 0 and config.getMinChargePercentage() >= config.getChargePercentage()):
        print("ACTION: Release control.")
        client.writeRegisters(40149, [0, 0], slave=3)
        client.writeRegisters(40151, [0, 803], slave=3)
        return

    client.writeRegisters(40151, [0, 802], slave=3)
    if rendament > 0:
        print(f"ACTION: Charge {rendament}")
        client.writeRegisters(40149, [65535, 65535 - rendament], slave=3)
    else:
        print(f"ACTION: Discharge {abs(rendament)}")
        client.writeRegisters(40149, [0, abs(rendament)], slave=3)

    return


def scheduleImplementation(client: ModbusClient):
    """
    ### Automate a schedule

    Will read a schedule in from setting.schedule(: str[]) and execute the expected actions following the schedule.
    """
    schedule = config.getSchedule()
    previousKey = None

    # Loop
    while True:
        currentTime = config.getCurrentTime()
        hour = currentTime.hour
        minutes = math.floor(currentTime.minute / 15) * 15
        key = f"h{hour:02}"
        minuteKey = f"m{minutes:02}"
        currentAction = schedule.get(key).get(minuteKey)

        if f"{key}{minuteKey}" == previousKey:
            continue

        # print hour marks to show progress
        print(f"Current Time: {currentTime.hour}:{minutes:02}")
        previousKey = f"{key}{minuteKey}"

        if currentAction == None:
            sendToInverter(client, False, 0)
            print("Schedule has ended. Restart addon to restart the schedule")
        else:
            if currentAction.power == 0:
                sendToInverter(client, False, 0)
            else:
                sendToInverter(client, True, currentAction.power)

        # Sleep for half a minute before starting the next round.
        time.sleep(60)

def main():
    client = ModbusClient()
    client.connect()

    try:
        mode = config.getControlMode()
        if mode == ControlMode.NONE:
            sendToInverter(client, False, 0)
        elif mode == ControlMode.CHARGE:
            sendToInverter(client, True, 5000)
        elif mode == ControlMode.DISCHARGE:
            sendToInverter(client, True, -5000)
        elif mode == ControlMode.SCHEDULE:
            scheduleImplementation(client)
        else:
            raise Exception("Unknown control mode \"" + mode.name + '"')
    finally:
        client.close()

if __name__ == "__main__":
    main()
    time.sleep(10)
