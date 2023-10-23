
import pyasge
from game.gamestates.gamestate import GameStateID
from game.gamestates.gameplay import GamePlay
from game.gamestates.gamemenu import GameMenu
from game.gamestates.gamewon import GameWon
from game.gamestates.gameover import GameOver


def update(self, game_time: pyasge.GameTime) -> None:
    # delegate the update logic to the active state
    new_state = self.current_state.update(game_time)
    if self.current_state.id != new_state:
        if new_state is GameStateID.START_MENU:
            self.current_state = GameMenu(self.data)
        elif new_state is GameStateID.GAMEPLAY:
            self.current_state = GamePlay(self.data)
        elif new_state is GameStateID.GAME_OVER:
            self.current_state = GameOver(self.data)
        elif new_state is GameStateID.WINNER_WINNER:
            self.current_state = GameWon(self.data)
