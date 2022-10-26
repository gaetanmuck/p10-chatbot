
class ConvState:



    def __init__(self):
        self.step = 'init'



    @property
    def CurrentPos(self):
        return self.step
    @CurrentPos.setter
    def setStep(self, current):
        self.step = current