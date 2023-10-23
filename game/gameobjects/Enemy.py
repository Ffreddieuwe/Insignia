from game.gameobjects.behaviourtree import EnemyState
from game.gameobjects.behaviourtree import eye_bt
from game.gameobjects.behaviourtree import goblin_bt
from game.gameobjects.behaviourtree import skeleton_bt
from game.gameobjects.behaviourtree import mushroom_bt
import pyasge
from abc import ABC
from game.gamedata import GameData
from pyfmodex.flags import MODE


class Enemy(ABC):
    # Initialises Variables
    def __init__(self, data: GameData):
        # Current state
        self.frame_quantity = None
        self.state = EnemyState.Idle
        self.id = None

        self.attacked = False
        self.moved = False
        self.attack_finish = False

        self.data = data
        self.sounds = {
            "attack": self.data.audio_system.create_sound("data/Music/DESIGNED-GRAB-BLOCK-THROW-1.wav", mode=MODE.LOOP_OFF)}

        # Sprites and animation variables
        self.sprite_list = None
        self.sprite = pyasge.Sprite()
        self.animation_state = None
        self.animation_frame = 1
        self.animation_timer = 0
        self.animation_bump = 1

        # AI variables for BT
        self.can_fly = False
        self.hit_and_run = False
        self.detection = 10
        self.destination = []
        self.player_distance = 100
        self.base_distance = None
        self.target = pyasge.Point2D(0, 0)
        self.targeted_player = None
        self.locked = False

    # Sets appropriate animation for current state
    def set_animation_state(self):
        if self.state == EnemyState.Idle:
            self.animation_state = 1
        elif self.state == EnemyState.Attacking:
            self.animation_state = 0
        elif self.state == EnemyState.Run_Away or self.state == EnemyState.Run_Towards:
            self.animation_state = 2
        elif self.state == EnemyState.Take_Damage:
            self.animation_state = 3

    # Renders sprite
    def render(self, renderer: pyasge.Renderer, game_time: pyasge.GameTime) -> None:
        renderer.render(self.sprite)

    # Runs animation appropriate for animation state
    def run_animation(self, game_time: pyasge.GameTime):
        self.animation_timer += game_time.frame_time

        if self.animation_timer > 0.2:
            if self.animation_frame >= self.frame_quantity[self.animation_state] - 1:
                if self.animation_state == 0:
                    self.animation_state = 1
                    self.attack_finish = True
                    self.state = EnemyState.Idle
                self.animation_frame = 1
            else:
                self.animation_frame += 1

            if self.animation_state == 1:
                self.sprite.y += self.animation_bump
                self.animation_bump = -self.animation_bump

            self.sprite.loadTexture(self.sprite_list[self.animation_state][self.animation_frame])
            self.animation_timer = 0

    def move(self, data: GameData):
        if self.state == EnemyState.Run_Towards or self.state == EnemyState.Run_Away:
            if len(self.destination) > 0:
                if int(self.sprite.x) > int(self.destination[0].x):
                    self.sprite.flip_flags = pyasge.Sprite.FlipFlags.FLIP_X
                    self.sprite.x -= 1
                elif int(self.sprite.x) < int(self.destination[0].x):
                    self.sprite.flip_flags = pyasge.Sprite.FlipFlags.NORMAL
                    self.sprite.x += 1
                elif int(self.sprite.y) > int(self.destination[0].y):
                    self.sprite.y -= 1
                elif int(self.sprite.y) < int(self.destination[0].y):
                    self.sprite.y += 1
                else:
                    self.destination.pop(0)
                    if len(self.destination) == 1:
                        self.destination.pop(0)
                        self.animation_state = 1
                        self.animation_frame = 0


class Goblin(Enemy):
    # Initialises unique variables
    def __init__(self, data: GameData):
        super().__init__(data)
        self.health = 10
        self.damage = 2
        self.hit_and_run = True
        self.start = None

        self.sprite_list = [["/data/textures/Enemies/Goblin/Attack/goblin_attack_1.png",
                             "/data/textures/Enemies/Goblin/Attack/goblin_attack_2.png",
                             "/data/textures/Enemies/Goblin/Attack/goblin_attack_3.png",
                             "/data/textures/Enemies/Goblin/Attack/goblin_attack_4.png",
                             "/data/textures/Enemies/Goblin/Attack/goblin_attack_5.png",
                             "/data/textures/Enemies/Goblin/Attack/goblin_attack_6.png",
                             "/data/textures/Enemies/Goblin/Attack/goblin_attack_7.png",
                             "/data/textures/Enemies/Goblin/Attack/goblin_attack_8.png"
                             ],
                            ["/data/textures/Enemies/Goblin/Idle/goblin_idle_1.png",
                             "/data/textures/Enemies/Goblin/Idle/goblin_idle_2.png",
                             "/data/textures/Enemies/Goblin/Idle/goblin_idle_3.png",
                             "/data/textures/Enemies/Goblin/Idle/goblin_idle_4.png"
                             ],
                            ["/data/textures/Enemies/Goblin/Move/goblin_move_1.png",
                             "/data/textures/Enemies/Goblin/Move/goblin_move_2.png",
                             "/data/textures/Enemies/Goblin/Move/goblin_move_3.png",
                             "/data/textures/Enemies/Goblin/Move/goblin_move_4.png",
                             "/data/textures/Enemies/Goblin/Move/goblin_move_5.png",
                             "/data/textures/Enemies/Goblin/Move/goblin_move_6.png",
                             "/data/textures/Enemies/Goblin/Move/goblin_move_7.png",
                             "/data/textures/Enemies/Goblin/Move/goblin_move_8.png"
                             ],
                            ["/data/textures/Enemies/Goblin/Take Hit/goblin_damage_1.png",
                             "/data/textures/Enemies/Goblin/Take Hit/goblin_damage_2.png",
                             "/data/textures/Enemies/Goblin/Take Hit/goblin_damage_3.png",
                             "/data/textures/Enemies/Goblin/Take Hit/goblin_damage_4.png"
                             ]
                            ]
        self.frame_quantity = [8, 4, 8, 4]

    def get_state(self):
        goblin_bt(self)
        self.set_animation_state()


class Eye(Enemy):
    def __init__(self, data: GameData):
        super().__init__(data)
        self.health = 8
        self.detection = 13
        self.damage = 2
        self.can_fly = True

        self.sprite_list = [["/data/textures/Enemies/Flying_Eye/Attack/eye_attack_1.png",
                             "/data/textures/Enemies/Flying_Eye/Attack/eye_attack_2.png",
                             "/data/textures/Enemies/Flying_Eye/Attack/eye_attack_3.png",
                             "/data/textures/Enemies/Flying_Eye/Attack/eye_attack_4.png",
                             "/data/textures/Enemies/Flying_Eye/Attack/eye_attack_5.png",
                             "/data/textures/Enemies/Flying_Eye/Attack/eye_attack_6.png",
                             "/data/textures/Enemies/Flying_Eye/Attack/eye_attack_7.png",
                             "/data/textures/Enemies/Flying_Eye/Attack/eye_attack_8.png"
                             ],
                            ["/data/textures/Enemies/Flying_Eye/Idle/eye_idle_1.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_2.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_3.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_4.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_5.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_6.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_7.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_8.png"
                             ],
                            ["/data/textures/Enemies/Flying_Eye/Idle/eye_idle_1.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_2.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_3.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_4.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_5.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_6.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_7.png",
                             "/data/textures/Enemies/Flying_Eye/Idle/eye_idle_8.png"
                             ],
                            ["/data/textures/Enemies/Flying_Eye/Take Hit/eye_damage_1.png",
                             "/data/textures/Enemies/Flying_Eye/Take Hit/eye_damage_2.png",
                             "/data/textures/Enemies/Flying_Eye/Take Hit/eye_damage_3.png",
                             "/data/textures/Enemies/Flying_Eye/Take Hit/eye_damage_4.png"
                             ]
                            ]
        self.frame_quantity = [8, 8, 8, 4]

    def get_state(self):
        eye_bt(self)
        self.set_animation_state()


class Skeleton(Enemy):
    def __init__(self, data: GameData):
        super().__init__(data)
        self.health = 15
        self.damage = 4

        self.sprite_list = [["/data/textures/Enemies/Skeleton/Attack/skeleton_attack_1.png",
                             "/data/textures/Enemies/Skeleton/Attack/skeleton_attack_2.png",
                             "/data/textures/Enemies/Skeleton/Attack/skeleton_attack_3.png",
                             "/data/textures/Enemies/Skeleton/Attack/skeleton_attack_4.png",
                             "/data/textures/Enemies/Skeleton/Attack/skeleton_attack_5.png",
                             "/data/textures/Enemies/Skeleton/Attack/skeleton_attack_6.png",
                             "/data/textures/Enemies/Skeleton/Attack/skeleton_attack_7.png",
                             "/data/textures/Enemies/Skeleton/Attack/skeleton_attack_8.png"
                             ],
                            ["/data/textures/Enemies/Skeleton/Idle/skeleton_idle_1.png",
                             "/data/textures/Enemies/Skeleton/Idle/skeleton_idle_2.png",
                             "/data/textures/Enemies/Skeleton/Idle/skeleton_idle_3.png",
                             "/data/textures/Enemies/Skeleton/Idle/skeleton_idle_4.png"
                             ],
                            ["/data/textures/Enemies/Skeleton/Move/skeleton_move_1.png",
                             "/data/textures/Enemies/Skeleton/Move/skeleton_move_2.png",
                             "/data/textures/Enemies/Skeleton/Move/skeleton_move_3.png",
                             "/data/textures/Enemies/Skeleton/Move/skeleton_move_4.png"
                             ],
                            ["/data/textures/Enemies/Skeleton/Take Hit/skeleton_damage_1.png",
                             "/data/textures/Enemies/Skeleton/Take Hit/skeleton_damage_2.png",
                             "/data/textures/Enemies/Skeleton/Take Hit/skeleton_damage_3.png",
                             "/data/textures/Enemies/Skeleton/Take Hit/skeleton_damage_4.png"
                             ]
                            ]
        self.frame_quantity = [8, 4, 4, 4]

    def get_state(self):
        skeleton_bt(self)
        self.set_animation_state()


class Mushroom(Enemy):
    def __init__(self, data: GameData):
        super().__init__(data)
        self.health = 20
        self.damage = 5

        self.frame_quantity = [8, 4, 8, 4]
        self.sprite_list = [["/data/textures/Enemies/Mushroom/Attack/mushroom_attack_1.png",
                             "/data/textures/Enemies/Mushroom/Attack/mushroom_attack_2.png",
                             "/data/textures/Enemies/Mushroom/Attack/mushroom_attack_3.png",
                             "/data/textures/Enemies/Mushroom/Attack/mushroom_attack_4.png",
                             "/data/textures/Enemies/Mushroom/Attack/mushroom_attack_5.png",
                             "/data/textures/Enemies/Mushroom/Attack/mushroom_attack_6.png",
                             "/data/textures/Enemies/Mushroom/Attack/mushroom_attack_7.png",
                             "/data/textures/Enemies/Mushroom/Attack/mushroom_attack_8.png"
                             ],
                            ["/data/textures/Enemies/Mushroom/Idle/mushroom_idle_1.png",
                             "/data/textures/Enemies/Mushroom/Idle/mushroom_idle_2.png",
                             "/data/textures/Enemies/Mushroom/Idle/mushroom_idle_3.png",
                             "/data/textures/Enemies/Mushroom/Idle/mushroom_idle_4.png"
                             ],
                            ["/data/textures/Enemies/Mushroom/Move/mushroom_move_1.png",
                             "/data/textures/Enemies/Mushroom/Move/mushroom_move_2.png",
                             "/data/textures/Enemies/Mushroom/Move/mushroom_move_3.png",
                             "/data/textures/Enemies/Mushroom/Move/mushroom_move_4.png",
                             "/data/textures/Enemies/Mushroom/Move/mushroom_move_5.png",
                             "/data/textures/Enemies/Mushroom/Move/mushroom_move_6.png",
                             "/data/textures/Enemies/Mushroom/Move/mushroom_move_7.png",
                             "/data/textures/Enemies/Mushroom/Move/mushroom_move_8.png"
                             ],
                            ["/data/textures/Enemies/Mushroom/Take Hit/mushroom_damage_1.png",
                             "/data/textures/Enemies/Mushroom/Take Hit/mushroom_damage_2.png",
                             "/data/textures/Enemies/Mushroom/Take Hit/mushroom_damage_3.png",
                             "/data/textures/Enemies/Mushroom/Take Hit/mushroom_damage_4.png"
                             ]
                            ]

    def get_state(self):
        mushroom_bt(self)
        self.set_animation_state()
