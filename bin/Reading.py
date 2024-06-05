
from random import randint
from State import State

class Reading(State):
    def __init__(self,state_machine):
        super().__init__(state_machine)
    def enter(self,args):
        print("Reading Card")
    def loop(self):
        if (randint(0,100))%100 != 99:
            card_value = [randint(-1, 500)]
            self._state_machine.set(self._state_machine.STATE_SORTING, card_value)
        else:
            self._state_machine.set(self._state_machine.STATE_WAITING)
