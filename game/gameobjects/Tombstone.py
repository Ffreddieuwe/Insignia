import pyasge


class Tombstone:
    def __init__(self, x, y, filename, scale):
        self.sprite = pyasge.Sprite()
        self.sprite.loadTexture(filename)
        self.sprite.scale = scale
        self.sprite.x = x
        self.sprite.y = y
