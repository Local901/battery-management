from pymodbus.client import ModbusTcpClient
from config import settings
from homeAssistant import HomeAssistant

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

    if not active:
        client.write_registers(40149, [0, 0], slave=3)
        client.write_registers(40151, [0, 803], slave=3)
        return

    client.write_registers(40151, [0, 802], slave=3)
    # TODO: The 0 has to be solar charge power
    client.write_registers(40149, [65535, 65535 - rendament], slave=3)
    return

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
            sendToInverter(client, False, 100)
        if settings["control_mode"] == "manual":
            sendToInverter(client, bool(settings["manual"]["charge_battery"]), 100)
    finally:
        client.close()

if __name__ == "__main__":
    main()
