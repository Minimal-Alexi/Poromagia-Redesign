from StateMachine import StateMachine

if __name__ == "__main__":
    state_machine = StateMachine()
    state_machine.set(state_machine.STATE_WAITING)
    while True:
        state_machine.run()