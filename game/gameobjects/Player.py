import pyasge
from game.gamedata import GameData


class player:
    def __init__(self, data: GameData):
        # Movement variables
        self.destination = []
        self.id = None
        self.current_tile = None
        self.is_moving = False
        self.do_animation = True
        self.move_target = pyasge.Point2D(0, 0)
        self.selected = False
        self.moved = False
        self.attacked = False
        self.targeted_enemy = None

        self.hp = 15
        self.damage = 4
        self.data = data

        # Sprite and animation variables
        self.sprite = pyasge.Sprite()
        self.animation_state = 1
        self.animation_frame = 0
        self.animation_timer = 0
        self.sprite_list = ["data/textures/player assets/Knight2.0/_AttackNoMovement 2.0.png",
                            "data/textures/player assets/Knight2.0/_Idle 2.0.png",
                            "data/textures/player assets/Knight2.0/_Run 2.0.png"]
        self.anim_frames = [4, 10, 10]
        self.width_list = [80, 19, 28]
        self.steps = [120, 120, 120]
        self.start = [28, 45, 43]
        self.sprite_x = self.start[self.animation_state]
        self.sprite.z_order = 10
        self.sprite_width = self.width_list[self.animation_state]
        self.sprite.loadTexture(self.sprite_list[self.animation_state])
        self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = self.sprite_x
        self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = self.sprite_width
        self.sprite.width = self.sprite_width
        self.sprite.height = self.sprite.height

    def run_animation(self, game_time: pyasge.GameTime):
        self.animation_timer += game_time.frame_time

        if self.animation_timer > 0.1:

            if self.animation_frame >= self.anim_frames[self.animation_state] - 1:
                if self.animation_state == 0:
                    self.animation_state = 1
                self.animation_frame = 0
                self.sprite_x = self.start[self.animation_state]
                self.sprite_width = self.width_list[self.animation_state]

            else:
                self.animation_frame += 1
                self.sprite_x = self.start[self.animation_state] + \
                                (self.animation_frame * self.steps[self.animation_state])

            self.sprite.loadTexture(self.sprite_list[self.animation_state])
            self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.START_X] = self.sprite_x
            self.sprite.src_rect[pyasge.Sprite.SourceRectIndex.LENGTH_X] = self.sprite_width
            self.sprite.width = self.sprite_width
            self.animation_timer = 0

    def render(self, renderer: pyasge.Renderer, game_time: pyasge.GameTime) -> None:
        renderer.render(self.sprite)

    def move(self, data: GameData):
        if self.is_moving:
            self.current_tile = data.game_map.tile(pyasge.Point2D(self.sprite.x, self.sprite.y))
            if self.do_animation:
                self.animation_state = 2
                self.animation_frame = 0
                self.sprite_x = self.start[self.animation_state]
                self.sprite_width = self.width_list[self.animation_state]
                self.do_animation = False
            if len(self.destination) > 0:
                if int(self.sprite.x) > int(self.destination[0].x - self.sprite_width * 0.4):
                    self.sprite.flip_flags = pyasge.Sprite.FlipFlags.FLIP_X
                    self.sprite.x -= 2
                elif int(self.sprite.x) < int(self.destination[0].x - self.sprite_width * 0.4):
                    self.sprite.flip_flags = pyasge.Sprite.FlipFlags.NORMAL
                    self.sprite.x += 2
                elif int(self.sprite.y) > int(self.destination[0].y):
                    self.sprite.y -= 2
                elif int(self.sprite.y) < int(self.destination[0].y):
                    self.sprite.y += 2
                else:

                    self.destination.pop(0)
                    if len(self.destination) == 0:
                        self.animation_state = 1
                        self.animation_frame = 0
                        self.sprite_x = self.start[self.animation_state]
                        self.sprite_width = self.width_list[self.animation_state]
                        self.is_moving = False
                        self.do_animation = True
