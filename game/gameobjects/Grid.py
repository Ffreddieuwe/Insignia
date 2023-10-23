import pyasge


class grid:
    def __init__(self) -> None:
        self.sprite = pyasge.Sprite()
        self.sprite.loadTexture("data/textures/grid/grid.png")
        self.selecting = False
        self.visible = True
        self.reachable = False

    def render(self, renderer: pyasge.Renderer, game_time: pyasge.GameTime) -> None:
        renderer.render(self.sprite)
