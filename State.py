"""
State is a base class for all states.

Every state class must have the following methods:
- enter(): to initialize variables, set ui, set rotary encoder(press, rotate), etc. called when the state is entered
- loop(): called repeatedly until the state is changed

Setting next state:
- To set the next state, call state_machine.set(state_code, args)
- The state_code is defined in the StateMachine class, the data type is int
- The args is a list of arguments to pass to the next state. (to method enter())
"""
class State:
    def __init__(self, state_machine):
        self._state_machine = state_machine

    def enter(self, args):
        raise NotImplementedError("This method must be defined and overridden")

    def loop(self):
        raise NotImplementedError("This method must be defined and overridden")