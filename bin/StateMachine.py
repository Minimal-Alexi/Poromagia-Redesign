from Wait import Wait
from Reading import Reading
from Sorting import Sorting

class StateMachine():

    STATE_WAITING = 0
    STATE_READING = 1
    STATE_SORTING = 2

    state_dict = {STATE_WAITING:Wait,
        STATE_READING:Reading,
        STATE_SORTING:Sorting
    }
    def __init__(self):
        self._args = None
        self._switched = False
        self._state = None
        self._states = {}

    def get_state(self, state_class_obj):
        if state_class_obj not in self._states:
            self._states[state_class_obj] = state_class_obj(self)  # pass self to state class, to give property access
        return self._states[state_class_obj]
    def set(self,state_code, args = None):
        if args is not None and not isinstance(args, list):
            raise ValueError("args must be a list")
        try:
            self._args = args
            state = self.state_dict[state_code]
            self._state = self.get_state(state)
            self._switched = True
        except KeyError:
            raise ValueError("Invalid state code to switch to")

    def run(self):
        if self._switched:
            self._state.enter(self._args)
            self._switched = False
            return
        self._state.loop()