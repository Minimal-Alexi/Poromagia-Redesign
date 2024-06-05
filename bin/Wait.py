from State import State

class Wait(State):
    def __init__(self,state_machine):
        super().__init__(state_machine)
    def enter(self,args):
        print("Waiting for input")
    def loop(self):
        start = input()
        self._state_machine.set(self._state_machine.STATE_READING)
