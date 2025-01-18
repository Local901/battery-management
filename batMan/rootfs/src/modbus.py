from pymodbus.client import ModbusTcpClient
from config import config

class ModbusClient():

    def __init__(self):
        if config.getHost() == "127.1.1.1":
            # This is for development.
            self._client = None
        else:
            self._client = ModbusTcpClient(
                config.getHost(),
                port=config.getPort(),
                name="BatMan",
                reconnect_delay=str(config.getDelay()) + ".0",
                timeout=config.getTimeout(),
            )

    def connect(self):
        if (self._client == None):
            return
        self._client.connect()
        if not self._client.connected:
            raise Exception("Failed to make connection on: " + config.getHost() + ":" + str(config.getPort()))

    def close(self):
        if (self._client != None):
            self._client.close()

    def writeRegisters(self, address: int, values: list[int], *, slave: int = 1, no_response_expected: bool = False):
        if (self._client == None):
            print("DEBUG: Write registers: " + str(address) + "->" + str(values))
            return
        self._client.write_registers(
            address,
            values,
            slave=slave,
            no_response_expected=no_response_expected
        )
