
class Action():
    power = 0

    def __init__(self, power: int):
        self.power = power

    def __str__(self):
        if self.power == 0:
            return "None"
        if self.power > 0:
            return f"Charge => {self.power}"
        return f"Discharge => {self.power}"
    def __repr__(self):
        return self.__str__()
