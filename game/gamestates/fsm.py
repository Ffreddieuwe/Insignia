import pyasge


class FSM:
    """
    A simple FSM

    This simple class allows you to assign a function as a state.
    When the FSM is updated it will call the function for you. This
    is a versatile system and can be used as a "brain" in other
    classes.
    See: https://gamedevelopment.tutsplus.com/tutorials/finite-state-machines-theory-and-implementation--gamedev-11867
    """

    def __init__(self):
        """ Sets the state to None """
        self.current_state = None

    def setstate(self, state):
        """ Updates the function to call when updated """
        self.current_state = state

    def update(self, game_time: pyasge.GameTime):
        """ Calls the function assigned to current_state """
        if self.current_state is not None:
            self.current_state(game_time)
