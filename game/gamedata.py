import pyasge
import pyfmodex

class GameData:
    """
    GameData stores the data that needs to be shared

    When using multiple states in a game, you will find that
    some game data needs to be shared. GameData can be used to
    share access to data that the game and any running states may
    need.
    """

    def __init__(self) -> None:
        self.fonts = {}
        self.game_map = None
        self.audio_system = pyfmodex.System()
        self.bg_audio = None
        self.bg_audio_channel = None
        self.game_res = [1920, 1080]
        self.inputs = None
        self.gamepad = None
        self.prev_gamepad = None
        self.renderer = None
        self.shaders: dict[str, pyasge.Shader] = {}
        self.play_option = None
        self.exit_option = None

