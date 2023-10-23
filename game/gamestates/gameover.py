import pyasge

from game.gamestates.gamestate import GameState
from game.gamestates.gamestate import GameStateID
from game.gamedata import GameData


class GameOver(GameState):

    def __init__(self, data: GameData) -> None:
        super().__init__(data)
        self.id = GameStateID.GAME_OVER
        self.transition = False
        self.menu = True
        self.newgame = False
        self.play_option = None
        self.exit_option = None
        self.menu_text = None
        self.menu_option = 0
        self.data.background = pyasge.Sprite()
        self.button = pyasge.Sprite()
        self.button1 = pyasge.Sprite()
        self.button2 = pyasge.Sprite()
        self.initMenu()
        map_mid = [
            self.data.game_map.width * self.data.game_map.tile_size[0] * 0.5,
            self.data.game_map.height * self.data.game_map.tile_size[1] * 0.5
        ]

        self.camera = pyasge.Camera(map_mid, self.data.game_res[0], self.data.game_res[1])
        self.camera.zoom = 1
        self.ui_label = pyasge.Text(self.data.renderer.getDefaultFont(), "UI Label", 10, 50)
        self.ui_label.z_order = 120
        self.data.renderer.setClearColour(pyasge.COLOURS.DARKSLATEGRAY)

    def initMenu(self) -> bool:

        self.button2.loadTexture("data/textures/UI_Sprites/UI_Flat_Button_Large_Lock_01a2.png")
        self.button2.x = 800
        self.button2.y = 430

        self.button2.scale = 3.5
        self.button.loadTexture("data/textures/UI_Sprites/UI_Flat_Banner_01_Downward.png")
        self.button.x = 560
        self.button.y = 630
        self.button.scale = 3.5

        self.button1.loadTexture("data/textures/UI_Sprites/UI_Flat_Banner_01_Downward.png")
        self.button1.x = 1050
        self.button1.y = 630
        self.button1.scale = 3.5

        self.data.fonts["mainfont"] = self.data.renderer.loadFont("data/fonts/Kenney Future.ttf", 45)
        self.menu_text = pyasge.Text(self.data.fonts["mainfont"])
        self.menu_text.string = "You Lose!"
        self.menu_text.position = [830, 500]
        self.menu_text.colour = pyasge.COLOURS.BLACK

        self.play_option = pyasge.Text(self.data.fonts["mainfont"])
        self.play_option.string = ">Again"
        self.play_option.position = [630, 700]
        self.play_option.colour = pyasge.COLOURS.BLACK
        self.exit_option = pyasge.Text(self.data.fonts["mainfont"])
        self.exit_option.string = " Quit"
        self.exit_option.position = [1140, 700]
        self.exit_option.colour = pyasge.COLOURS.LIGHTSLATEGRAY
        return True


    def click_handler(self, event: pyasge.ClickEvent, data: GameData) -> None:
        pass

    def key_handler(self, event: pyasge.KeyEvent) -> None:
        if event.action == pyasge.KEYS.KEY_PRESSED:

            if event.key == pyasge.KEYS.KEY_RIGHT or event.key == pyasge.KEYS.KEY_LEFT:
                self.menu_option = 1 - self.menu_option
                if self.menu_option == 0:
                    self.play_option.string = ">Again"
                    self.play_option.colour = pyasge.COLOURS.BLACK
                    self.exit_option.string = " Quit"
                    self.exit_option.colour = pyasge.COLOURS.LIGHTSLATEGRAY
                else:
                    self.play_option.string = " Again"
                    self.play_option.colour = pyasge.COLOURS.LIGHTSLATEGRAY
                    self.exit_option.string = ">Quit"
                    self.exit_option.colour = pyasge.COLOURS.BLACK
            if event.key == pyasge.KEYS.KEY_ENTER:
                if self.menu_option == 0:
                    self.newgame = True
                else:
                    exit(0)

    def move_handler(self, event: pyasge.MoveEvent) -> None:
        pass

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        pass

    def update(self, game_time: pyasge.GameTime) -> GameStateID:
        """ If user_clicked go to game menu else return GAME_OVER """
        if self.newgame:
            return GameStateID.GAMEPLAY
        else:
            return GameStateID.GAME_OVER

    def render(self, game_time: pyasge.GameTime) -> None:
        """ Renders the game world and the UI """
        self.data.renderer.setViewport(pyasge.Viewport(0, 0, self.data.game_res[0], self.data.game_res[1]))
        self.data.renderer.setProjectionMatrix(self.camera.view)
        self.data.shaders["example"].uniform("rgb").set([1.0, 1.0, 0])
        self.render_ui()
        pass

    def render_ui(self) -> None:
        """ Render the UI elements and map to the whole window """
        # set a new view that covers the width and height of game
        camera_view = pyasge.CameraView(self.data.renderer.resolution_info.view)
        vp = self.data.renderer.resolution_info.viewport
        self.data.renderer.setProjectionMatrix(0, 0, vp.w, vp.h)
        self.data.renderer.render(self.menu_text)
        self.data.renderer.render(self.play_option)
        self.data.renderer.render(self.exit_option)
        self.data.renderer.render(self.button)
        self.data.renderer.render(self.button1)
        self.data.renderer.render(self.button2)

