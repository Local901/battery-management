
class Action():
    action = "none"
    power = 0

    def __init__(self, action: str, power: int):
        if (power != 0):
            self.action = action
        self.power = power

    def __str__(self):
        return f"{self.action} => {self.power}"
    def __repr__(self):
        return f"{self.action} => {self.power}"
