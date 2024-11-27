from pymodbus.client import ModbusTcpClient
from config import settings
from homeAssistant import HomeAssistant
from customTime import currentTime
from schedule import parseTimeFrame, TimeFrame
import time

# Inverter.WModCfg.WCtlComCfg.WCtlComAct
# Gewenste waarde
# Eff-+blindverm.reg. via commu.
# 802: Actief (Act)
# 803: Inactief (Ina)
# 1
# Installateur
# 40151
# 2
# U32
# TAGLIST
# WO

# Inverter.WModCfg.WCtlComCfg.WSpt
# Gewenste waarde
# Ingesteld rendement
# 1
# Installateur
# 40149
# 2
# S32
# FIX0
# WO

def sendToInverter(
    client: ModbusTcpClient,
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
        client.write_registers(40149, [0, 0], slave=3)
        client.write_registers(40151, [0, 803], slave=3)
        return

    client.write_registers(40151, [0, 802], slave=3)
    if rendament > 0:
        client.write_registers(40149, [65535, 65535 - rendament], slave=3)
    else:
        client.write_registers(40149, [0, abs(rendament)], slave=3)

    return


def autoImplementation(client: ModbusTcpClient):
    """
    ### Automate a schedule

    Will read a schedule in from setting.auto(: str[]) and execute the expected actions following the schedule.
    """
    frames: list[TimeFrame] = []

    # Load schedule frames
    for value in settings["auto"]:
        frames.append(parseTimeFrame(value))

    currentFrameIndex = -1

    # Find index of first frame with time falling before now
    for i in range(len(frames)):
        frame: list[TimeFrame] = frames[i]
        if frame.time.isBeforeNow():
            currentFrameIndex = i
        else:
            break

    # Loop
    while True:
        frame: TimeFrame = frames[currentFrameIndex] if currentFrameIndex >= 0 else None
        print(frames)
        if frame is None or frame.action == "0":
            sendToInverter(client, False, 0)
        elif frame.action == "c":
            sendToInverter(client, True, frame.power if frame.power > 10 else 5000)
        elif frame.action == "d":
            sendToInverter(client, True, -1 * (frame.power if frame.power > 10 else 5000))
        
        print(frames[currentFrameIndex + 1].time)
        if currentFrameIndex < (len(frames) - 1) and frames[currentFrameIndex + 1].time.isBeforeNow(frame.time):
            currentFrameIndex += 1

        if currentFrameIndex >= (len(frames) - 2):
            print("Automated schedule has finished. Restart addon to restart the schedule.")
            print("Last scheduled action will be active until restart.")

        # Sleep for half a minute before starting the next round.
        time.sleep(30)

def main():
    ha = HomeAssistant()
    client = ModbusTcpClient(
        settings["host"],
        port=settings["port"],
        name="BatMan",
        reconnect_delay=str(settings["delay"]) + ".0",
        timeout=settings["timeout"],
    )
    client.connect()
    if not client.connected:
        raise Exception("Failed to make connection on: " + settings["host"] + ":" + str(settings["port"]))

    try:
        if settings["control_mode"] == "none":
            sendToInverter(client, False, 0)
        elif settings["control_mode"] == "charge":
            sendToInverter(client, bool(settings["manual"]["charge_battery"]), 5000)
        elif settings["control_mode"] == "discharge":
            sendToInverter(client, bool(settings["manual"]["charge_battery"]), -5000)
        elif settings["control_mode"] == "auto":
            autoImplementation(client)
    finally:
        client.close()

if __name__ == "__main__":
    main()
