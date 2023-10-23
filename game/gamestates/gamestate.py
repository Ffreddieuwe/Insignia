import pyasge

from abc import ABC, abstractmethod
from enum import Enum
from game.gamedata import GameData


class GameStateID(Enum):
    """ All game states need IDs.

    You can use these ID's to transition between different
    game states. For example if the start menu state returns
    GAMEPLAY, you know you need to swap the active state out
    to start the game.
    """
    UNKNOWN = -1
    START_MENU = 1
    GAMEPLAY = 2
    GAME_OVER = 3
    WINNER_WINNER = 4


class GameState(ABC):
    """ A game state is an abstract class used to define states

    In order to make use of this class you should inherit from it
    and provide definitions for the functions below. You should
    not need to instantiate this class directly.
    """

    @abstractmethod
    def __init__(self, data: GameData) -> None:
        self.id = GameStateID.UNKNOWN
        self.data = data

    @abstractmethod
    def click_handler(self, event: pyasge.ClickEvent, data: GameData) -> None:
        pass

    @abstractmethod
    def key_handler(self, event: pyasge.KeyEvent) -> None:
        pass

    @abstractmethod
    def move_handler(self, event: pyasge.MoveEvent) -> None:
        pass

    @abstractmethod
    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        pass

    @abstractmethod
    def update(self, game_time: pyasge.GameTime) -> None:
        pass

    @abstractmethod
    def render(self, game_time: pyasge.GameTime) -> None:
        pass
