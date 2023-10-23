import random

import pyasge

from pyfmodex.flags import MODE
from game.gamedata import GameData
from game.gameobjects.gamemap import GameMap
from game.gamestates.gamemenu import GameMenu


class MyASGEGame(pyasge.ASGEGame):
    """The ASGE Game in Python."""

    def __init__(self, settings: pyasge.GameSettings):
        """
        The constructor for the game.

        The constructor is responsible for initialising all the needed
        subsystems,during the game's running duration. It directly
        inherits from pyasge.ASGEGame which provides the window
        management and standard game loop.

        :param settings: The game settings
        """

        self.data = GameData
        pyasge.ASGEGame.__init__(self, settings)
        self.data = GameData()
        self.renderer.setBaseResolution(self.data.game_res[0], self.data.game_res[1], pyasge.ResolutionPolicy.MAINTAIN)
        random.seed(a=None, version=2)

        self.data.game_map = GameMap(self.renderer, "data/map/tmx/GT101 Project map.tmx")
        self.data.inputs = self.inputs
        self.data.renderer = self.renderer
        self.data.shaders["example"] = self.data.renderer.loadPixelShader("/data/shaders/example_rgb.frag")
        self.data.prev_gamepad = self.data.gamepad = self.inputs.getGamePad()

        # set up the background and load the fonts for the game
        self.init_audio()
        self.init_fonts()

        # register the key and mouse click handlers for this class
        self.key_id = self.data.inputs.addCallback(pyasge.EventType.E_KEY, self.key_handler)
        self.mouse_id = self.data.inputs.addCallback(pyasge.EventType.E_MOUSE_CLICK, self.click_handler)
        self.mousemove_id = self.data.inputs.addCallback(pyasge.EventType.E_MOUSE_MOVE, self.move_handler)

        # start the game in the menu
        self.current_state = GameMenu(self.data)

    def init_audio(self) -> None:
        self.data.audio_system.init()
        self.data.bg_audio = self.data.audio_system.create_sound("data/Music/09-Meydan-Contemplate-the-stars.mp3", mode=MODE.LOOP_NORMAL)
        self.data.bg_audio_channel = self.data.audio_system.play_sound(self.data.bg_audio)
        self.data.bg_audio_channel.volume = 10
    def init_fonts(self) -> None:
        """Loads the game fonts."""
        pass

    def move_handler(self, event: pyasge.MoveEvent) -> None:
        """Handles the mouse movement and delegates to the active state."""
        self.current_state.move_handler(event)

    def click_handler(self, event: pyasge.ClickEvent) -> None:
        """Forwards click events on to the active state."""
        self.current_state.click_handler(event, self.data)

    def key_handler(self, event: pyasge.KeyEvent) -> None:
        """Forwards Key events on to the active state."""
        self.current_state.key_handler(event)
        if event.key == pyasge.KEYS.KEY_ESCAPE:
            self.signalExit()

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        """Processes fixed updates."""
        self.current_state.fixed_update(game_time)

        if self.data.gamepad.connected and self.data.gamepad.START:
            self.signalExit()

    from game.gamestates.state_update import update

    def render(self, game_time: pyasge.GameTime) -> None:
        """Renders the game state and mouse cursor"""
        self.current_state.render(game_time)
