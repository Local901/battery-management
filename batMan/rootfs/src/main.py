from modbus import ModbusClient
from config import config, ControlMode
from customTime import currentTime
from schedule import TimeFrame, parseTimeFrame
import time

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

    if not active or rendament == 0:
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


def autoImplementation(client: ModbusClient):
    """
    ### Automate a schedule

    Will read a schedule in from setting.schedule(: str[]) and execute the expected actions following the schedule.
    """
    frames: list[TimeFrame] = []
    for value in config.getSchedule():
        frames.append(parseTimeFrame(value))
    frames.insert(0, TimeFrame(currentTime(), '0'))

    currentFrameIndex = 0

    print(f"TIME: {frames[currentFrameIndex].time}")

    # Loop
    while True:
        frame: TimeFrame = frames[currentFrameIndex] if currentFrameIndex >= 0 else None

        if frame is None or frame.action == "0":
            sendToInverter(client, False, 0)
        elif frame.action == "c":
            sendToInverter(client, True, frame.power if frame.power > 10 else 5000)
        elif frame.action == "d":
            sendToInverter(client, True, -1 * (frame.power if frame.power > 10 else 5000))

        if currentFrameIndex < (len(frames) - 1) and frames[currentFrameIndex + 1].time.isBeforeNow(frame.time if frame is not None else None):
            print(f"TIME: {frames[currentFrameIndex + 1].time}")
            currentFrameIndex += 1

        if currentFrameIndex >= (len(frames) - 1):
            print("Automated schedule has finished. Restart addon to restart the schedule.")
            print("Last scheduled action will be active until restart.")

        # Sleep for half a minute before starting the next round.
        time.sleep(30)

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
            autoImplementation(client)
        else:
            raise Exception("Unknown control mode \"" + mode.name + '"')
    finally:
        client.close()

if __name__ == "__main__":
    main()
    time.sleep(10)
