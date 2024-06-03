from State import State

class Sorting(State):
    def __init__(self,state_machine):
        super().__init__(state_machine)
        self._card_value = None
    def enter(self,args):
        print("Sorting Card")
        self._card_value = args[0]
    def loop(self):
        print(self._card_value)
        self._state_machine.set(self._state_machine.STATE_READING)
