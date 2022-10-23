import string


class ConvState:
    def __init__(self):
        self.step = 'destination'

    @property
    def CurrentPos(self):
        return self.step
    @CurrentPos.setter
    def setStep(self, current:string):
        self.step = current



class UserModel:
    def __init__(self):
        self.destination = ""
        self.origin = ""
        self.go_date = ""
        self.back_date = ""
        self.budget = ""