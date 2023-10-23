import pyasge

from game.gamestates.gamestate import GameState
from game.gamestates.gamestate import GameStateID
from game.gamedata import GameData


class GameMenu(GameState):

    def __init__(self, gamedata: GameData) -> None:
        super().__init__(gamedata)
        self.id = GameStateID.START_MENU
        self.transition = False
        self.menu = True
        self.play_option = None
        self.exit_option = None
        self.menu_text = None
        self.menu_option = 0
        self.data.background = pyasge.Sprite()
        self.button = pyasge.Sprite()
        self.button1 = pyasge.Sprite()
        self.button2 = pyasge.Sprite()
        self.logo = pyasge.Sprite()
        self.data.renderer.setClearColour(pyasge.COLOURS.DARKSLATEGRAY)
        self.initMenu()

    def initMenu(self) -> bool:

        self.logo.loadTexture("data/textures/InsigniaLogo.png")
        self.logo.scale = 1.75
        self.button2.loadTexture("data/textures/UI_Sprites/UI_Flat_Button_Large_Lock_01a2.png")
        self.button2.x = 1390
        self.button2.y = 460
        self.button2.scale = 3.5
        self.button.loadTexture("data/textures/UI_Sprites/UI_Flat_Banner_01_Downward.png")
        self.button.x = 1170
        self.button.y = 620
        self.button.scale = 3.5
        self.button1.loadTexture("data/textures/UI_Sprites/UI_Flat_Banner_01_Downward.png")
        self.button1.x = 1570
        self.button1.y = 620
        self.button1.scale = 3.5

        self.data.fonts["mainfont"] = self.data.renderer.loadFont("data/fonts/Kenney Future.ttf", 45)
        self.menu_text = pyasge.Text(self.data.fonts["mainfont"])
        self.menu_text.string = "insignia"
        self.menu_text.position = [1450, 540]
        self.menu_text.colour = pyasge.COLOURS.BLACK

        self.play_option = pyasge.Text(self.data.fonts["mainfont"])
        self.play_option.string = ">START"
        self.play_option.position = [1230, 690]
        self.play_option.colour = pyasge.COLOURS.BLACK
        self.exit_option = pyasge.Text(self.data.fonts["mainfont"])
        self.exit_option.string = "EXIT"
        self.exit_option.position = [1655, 690]
        self.exit_option.colour = pyasge.COLOURS.LIGHTSLATEGRAY

        return True

    def click_handler(self, event: pyasge.ClickEvent, data: GameData) -> None:
        if event.button == pyasge.MOUSE.MOUSE_BTN1:
            self.transition = False

    def key_handler(self, event: pyasge.KeyEvent) -> None:
        if event.action == pyasge.KEYS.KEY_PRESSED:

            if event.key == pyasge.KEYS.KEY_RIGHT or event.key == pyasge.KEYS.KEY_LEFT:
                self.menu_option = 1 - self.menu_option
                if self.menu_option == 0:
                    self.play_option.string = ">START"
                    self.play_option.colour = pyasge.COLOURS.BLACK
                    self.exit_option.string = " EXIT"
                    self.exit_option.colour = pyasge.COLOURS.LIGHTSLATEGRAY
                else:
                    self.play_option.string = " START"
                    self.play_option.colour = pyasge.COLOURS.LIGHTSLATEGRAY
                    self.exit_option.string = ">EXIT"
                    self.exit_option.colour = pyasge.COLOURS.BLACK
            if event.key == pyasge.KEYS.KEY_ENTER:
                if self.menu_option == 0:
                    self.transition = True
                else:
                    exit(0)

    def move_handler(self, event: pyasge.MoveEvent) -> None:
        pass

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        pass

    def update(self, game_time: pyasge.GameTime) -> GameStateID:
        if self.transition:
            return GameStateID.GAMEPLAY

        return GameStateID.START_MENU

    def render(self, game_time: pyasge.GameTime) -> None:
        self.data.renderer.render(self.logo)
        self.data.renderer.render(self.button)
        self.data.renderer.render(self.button1)
        self.data.renderer.render(self.button2)
        self.data.renderer.render(self.menu_text)
        self.data.renderer.render(self.play_option)
        self.data.renderer.render(self.exit_option)
        pass
