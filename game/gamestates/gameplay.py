import random
import pyasge
from game.gamedata import GameData
from game.gamestates.gamestate import GameState
from game.gamestates.gamestate import GameStateID
from game.gameobjects.pathfinding import resolve
from game.gameobjects.pathfinding import distance_in_tiles
from game.gameobjects.Enemy import Goblin
from game.gameobjects.Enemy import Eye
from game.gameobjects.Enemy import Skeleton
from game.gameobjects.Enemy import Mushroom
from game.gameobjects.behaviourtree import EnemyState
from game.gameobjects.Player import player
from game.gameobjects.Grid import grid
from game.gameobjects.Tombstone import Tombstone


class GamePlay(GameState):
    def __init__(self, data: GameData) -> None:
        """ Creates the game world

        Use the constructor to initialise the game world in a "clean"
        state ready for the player. This includes resetting of player's
        health and the enemy positions.

        Args:
            data (GameData): The game's shared data
        """
        # Basic Setup
        super().__init__(data)

        # State Variables
        self.round_number = None
        self.transition = None
        self.menu = True
        self.id = GameStateID.GAMEPLAY

        # Win/Lose booleans
        self.lose = None
        self.game_win = None
        self.game_lose = None

        # UI variables
        self.button = pyasge.Sprite()
        self.button1 = pyasge.Sprite()
        self.button2 = pyasge.Sprite()
        self.button3 = pyasge.Sprite()
        self.button4 = pyasge.Sprite()
        self.quit_text = None

        self.button.z_order = 2
        self.button1.z_order = 2
        self.button2.z_order = 2
        self.button3.z_order = 2
        self.button4.z_order = 2

        # Turn variables
        self.current_round = None
        self.action_phase = False
        self.player_turn = True
        self.player_round = True
        self.next_round_instructions = None
        self.enemy_turn_over = False
        self.round = 1

        # Camera setup
        self.camera_vector = pyasge.Point2D(0, 0)
        self.camera_zoom = 0
        map_mid = [
            self.data.game_map.width * self.data.game_map.tile_size[0] * 0.5,
            (self.data.game_map.height * self.data.game_map.tile_size[1] * 0.5) + 600
        ]
        self.camera = pyasge.Camera(map_mid, self.data.game_res[0], self.data.game_res[1])
        self.camera.zoom = 1.5

        # Player init
        self.player_number = 0
        self.player_deploy_cost = 5
        self.player_list = []
        self.player_health = None
        self.tombstones = []
        x = 0
        while x < 3:
            self.player_list.append(player(data))
            self.player_list[x].__init__(data)
            self.player_list[x].sprite.scale = 1
            self.player_list[x].sprite.x = 500 + (100 * x)
            self.player_list[x].sprite.y = 1550
            self.player_list[x].sprite.z_order = 1
            self.player_list[x].current_tile = self.data.game_map.tile(
                pyasge.Point2D(self.player_list[x].sprite.x, self.player_list[x].sprite.y))
            x += 1
            self.player_list[x - 1].id = x


        # Enemy init
        self.enemy_list = []
        self.enemy_list.append(Goblin(data))
        self.enemy_list.append(Mushroom(data))
        self.enemy_list.append(Eye(data))
        self.enemy_list.append(Skeleton(data))
        for x in self.enemy_list:
            x.__init__(data)
            x.base_distance = distance_in_tiles(pyasge.Point2D(x.sprite.x, x.sprite.y), pyasge.Point2D(1100, 128), data)
            x.target.x = self.player_list[0].sprite.x
            x.target.y = self.player_list[0].sprite.y
            x.player_distance = distance_in_tiles(pyasge.Point2D(x.sprite.x, x.sprite.y),
                                                  pyasge.Point2D(x.target.x, x.target.y),
                                                  data)
            x.sprite.z_order = 1
            if not isinstance(x, Skeleton):
                x.sprite.scale = 0.75
            else:
                x.sprite.scale = 0.6

        self.enemy_spawn()

        self.grid_list = []
        while len(self.grid_list) != (40 * 60):
            self.grid_list.append(grid())

        for i in range(40):
            for j in range(60):
                self.grid_list[i * 60 + j].sprite.scale = 2
                self.grid_list[i * 60 + j].sprite.x = i * self.data.game_map.tile_size[0]
                self.grid_list[i * 60 + j].sprite.y = j * self.data.game_map.tile_size[1]
                self.grid_list[i * 60 + j].sprite.z_order = 0

        for rect in self.data.game_map.noGoArea:
            for grids in self.grid_list:
                if grids.sprite.x /2 < rect[0] + rect[2] and grids.sprite.x /2 + grids.sprite.width /2 > rect[0]:
                    if grids.sprite.y /2 < rect[1]+ rect[3] and grids.sprite.y /2 + grids.sprite.height /2> rect[1]:
                        grids.visible = False

        self.shaders = self.data.renderer.loadPixelShader("data/shaders/example_rgb.frag")

        self.data.renderer.setClearColour(pyasge.COLOURS.CORAL)
        self.init_ui()
        self.initMenu()

    def initMenu(self) -> bool:
        # Initialise Menu Elements
        self.data.fonts["mainfont"] = self.data.renderer.loadFont("data/fonts/Kenney Future.ttf", 45)
        self.next_round_instructions = pyasge.Text(self.data.fonts["mainfont"])
        self.next_round_instructions.string = "Press Space For\n Next Round"
        self.next_round_instructions.scale = 0.5
        self.next_round_instructions.position = [1550, 1000]
        self.next_round_instructions.colour = pyasge.COLOURS.BLACK
        self.next_round_instructions.z_order = 5

        self.quit_text = pyasge.Text(self.data.fonts["mainfont"])
        self.quit_text.string = "Escape to Quit"
        self.quit_text.scale = 0.5
        self.quit_text.position = [1560, 80]
        self.quit_text.colour = pyasge.COLOURS.BLACK
        self.quit_text.z_order = 5

        self.current_round = pyasge.Text(self.data.fonts["mainfont"])
        self.current_round.string = "Player Turn"
        self.current_round.scale = 0.5
        self.current_round.position = [670, 80]
        self.current_round.colour = pyasge.COLOURS.BLACK
        self.current_round.z_order = 5

        self.round_number = pyasge.Text(self.data.fonts["mainfont"])
        self.round_number.string = "Round: " + str(self.round)
        self.round_number.scale = 0.5
        self.round_number.position = [310, 80]
        self.round_number.colour = pyasge.COLOURS.BLACK
        self.round_number.z_order = 5

        self.player_health = pyasge.Text(self.data.fonts["mainfont"])
        self.player_health.string = " "
        self.player_health.scale = 0.5
        self.player_health.position = [75, 950]
        self.player_health.colour = pyasge.COLOURS.BLACK
        self.player_health.z_order = 5


        return True

    def init_ui(self):
        """Initialises the UI elements"""
        self.button.loadTexture("data/textures/UI_Sprites/UI_Flat_Banner_01_Downward.png")
        self.button.x = 200
        self.button.y = 20
        self.button.scale = 3.5

        self.button1.loadTexture("data/textures/UI_Sprites/UI_Flat_Banner_01_Downward.png")
        self.button1.x = 600
        self.button1.y = 20
        self.button1.scale = 3.5

        self.button2.loadTexture("data/textures/UI_Sprites/UI_Flat_Banner_01_Downward.png")
        self.button2.x = 1500
        self.button2.y = 20
        self.button2.scale = 3.5

        self.button3.loadTexture("data/textures/UI_Sprites/UI_Flat_Button_Large_Lock_01a2.png")
        self.button3.x = 55
        self.button3.y = 900
        self.button3.scale = 5

        self.button4.loadTexture("data/textures/UI_Sprites/UI_Flat_Button_Large_Lock_01a2.png")
        self.button4.x = 1520
        self.button4.y = 940
        self.button4.scale = 3.5
        pass

    def click_handler(self, event: pyasge.ClickEvent, data: GameData) -> None:
        for pc in self.player_list:
            if event.button is pyasge.MOUSE.MOUSE_BTN1 and \
                    event.action is pyasge.MOUSE.BUTTON_PRESSED:
                temp_bool = True
                for pc1 in self.player_list:
                    if pc1.animation_state == 2:
                        temp_bool = False

                if temp_bool:
                    if (event.x > pc.sprite.x) and (event.x < pc.sprite.x + pc.sprite.width):
                        if (event.y > pc.sprite.y) and (event.y < pc.sprite.y + pc.sprite.height):
                            for pc1 in self.player_list:
                                if pc1.selected:
                                    pc1.selected = False
                            pc.selected = True

            if event.button is pyasge.MOUSE.MOUSE_BTN2 and \
                    event.action is pyasge.MOUSE.BUTTON_PRESSED:
                if pc.selected:
                    for x in self.enemy_list:
                        if (event.x > x.sprite.x) and (event.x < x.sprite.x + x.sprite.width) \
                                and (event.y > x.sprite.y) and (event.y < x.sprite.y + x.sprite.height):
                            if distance_in_tiles(pyasge.Point2D(x.sprite.x, x.sprite.y),
                                                 pyasge.Point2D(pc.sprite.x, pc.sprite.y), data) < 3:
                                if not pc.attacked:
                                    x.health -= pc.damage
                                    pc.animation_frame = 1
                                    pc.animation_state = 0
                                    pc.sprite_x = pc.start[pc.animation_state]
                                    pc.sprite_width = pc.width_list[pc.animation_state]
                                    pc.attacked = True
                            elif not pc.moved:
                                pc.current_tile = data.game_map.tile(pyasge.Point2D(pc.sprite.x, pc.sprite.y))
                                new_dest = pyasge.Point2D(x.sprite.x, x.sprite.y - pc.sprite.height)
                                reachable_tile_list = []
                                if pc.current_tile != data.game_map.tile(new_dest):

                                    if distance_in_tiles(pyasge.Point2D(pc.sprite.x, pc.sprite.y), new_dest, data) > 2 and distance_in_tiles(pyasge.Point2D(pc.sprite.x, pc.sprite.y), new_dest, data) < 15:
                                        if data.game_map.costs[data.game_map.tile(new_dest)[1]][data.game_map.tile(pyasge.Point2D(new_dest))[0]] < 2:
                                            pc.is_moving = True
                                            pc.animation_frame = 1
                                            pc.animation_state = 2
                                            pc.sprite_x = pc.start[pc.animation_state]
                                            pc.sprite_width = pc.width_list[pc.animation_state]
                                            pc.destination = resolve(new_dest, self.data, pc, 0)
                                            pc.moved = True
                        elif not pc.moved:
                            # Starts player movement
                            pc.current_tile = data.game_map.tile(pyasge.Point2D(pc.sprite.x, pc.sprite.y))
                            new_dest = pyasge.Point2D(event.x, event.y - pc.sprite.height)

                            if pc.current_tile != data.game_map.tile(new_dest):
                                if distance_in_tiles(pyasge.Point2D(pc.sprite.x, pc.sprite.y), new_dest, data) < 15:
                                    if data.game_map.costs[data.game_map.tile(new_dest)[1]][data.game_map.tile(pyasge.Point2D(new_dest))[0]] < 2:
                                        pc.is_moving = True
                                        pc.animation_frame = 1
                                        pc.animation_state = 2
                                        pc.sprite_x = pc.start[pc.animation_state]
                                        pc.sprite_width = pc.width_list[pc.animation_state]
                                        pc.destination = resolve(new_dest, self.data, pc, 0)
                                        pc.moved = True

        '''
        if event.button is pyasge.MOUSE.MOUSE_BTN1 and \
                event.action is pyasge.MOUSE.BUTTON_PRESSED and self.player_turn:
            if not self.action_phase:
                if self.player_deploy_cost > 0:
                    for rect in self.data.game_map.playerBase:
                        if (pyasge.Point2D(event.x / 2, event.y / 2).x > rect[0]) and (
                                pyasge.Point2D(event.x / 2, event.y / 2).x < rect[0] + rect[2]):
                            if (pyasge.Point2D(event.x / 2, event.y / 2).y > rect[1]) and (
                                    pyasge.Point2D(event.x / 2, event.y / 2).y < rect[1] + rect[3]):
                                self.player_number += 1
                                self.player_deploy_cost -= pc.deploy_cost
                                self.player_list.append(player(data))
                                self.player_list[self.player_number].sprite.x = event.x
                                self.player_list[self.player_number].sprite.y = event.y
        '''

    def move_handler(self, event: pyasge.MoveEvent) -> None:
        """ Listens for mouse movement events from the game engine """
        for pc in self.player_list:
            if pc.selected:
                temp_bool = True
                for pc2 in self.player_list:
                    if pc2.is_moving:
                        temp_bool = False
                if temp_bool:
                    for x in self.grid_list:
                        # 15 is the width of the cursor
                        if distance_in_tiles(pyasge.Point2D(pc.sprite.x, pc.sprite.y), pyasge.Point2D(event.x,event.y), self.data) < 15:
                            if x.sprite.x <= event.x < x.sprite.x + x.sprite.width + 15 and x.sprite.y < event.y <= x.sprite.y + x.sprite.height + 15:
                                x.selecting = True
                            else:
                                x.selecting = False
                        else:
                            x.selecting = False
                else:
                    for x in self.grid_list:
                        x.selecting = False
        pass

    def key_handler(self, event: pyasge.KeyEvent) -> None:
        if event.action == pyasge.KEYS.KEY_PRESSED:
            if event.key == pyasge.KEYS.KEY_W:
                self.camera_vector.y = -10
            elif event.key == pyasge.KEYS.KEY_S:
                self.camera_vector.y = 10

            if event.key == pyasge.KEYS.KEY_SPACE:
                can_transition = True
                for pc in self.player_list:
                    if pc.animation_state != 1:
                        can_transition = False

                if self.player_turn and can_transition:
                    for x in self.enemy_list:
                        if isinstance(x, Goblin):
                            x.hit_and_run = True

                        x.target = pyasge.Point2D(0, 0)
                        x.targeted_player = None
                        x.destination = []
                        x.animation_frame = 1
                        x.attacked = False
                        x.moved = False
                    self.player_turn = False
                    self.action_phase = False
                    self.current_round.string = "Enemy Turn"

            pass

        elif event.action == pyasge.KEYS.KEY_RELEASED:
            if event.key == pyasge.KEYS.KEY_W:
                self.camera_vector.y = 0
            elif event.key == pyasge.KEYS.KEY_S:
                self.camera_vector.y = 0

            pass

    def enemy_spawn(self) -> None:
        random_spawns = random.sample(self.data.game_map.enemySpawn, 4)
        for enemy in self.enemy_list:
            x, y = random_spawns.pop()
            enemy.sprite.x = x * 2
            enemy.sprite.y = y * 2

    def fixed_update(self, game_time: pyasge.GameTime) -> None:
        """ Simulates deterministic time steps for the game objects"""
        pass

    def update(self, game_time: pyasge.GameTime) -> GameStateID:
        self.check_win_lose()
        self.player_health.string = " "
        for x in self.player_list:
            if x.selected:
                self.player_health.string = "Selected Unit: " + str(x.id) + "\nHealth:" + str(x.hp) \
                                            + "\nHas Moved: " + str(x.moved) + "\nHas Attacked: " + str(x.attacked)

        self.update_camera()
        if self.transition:
            return GameStateID.WINNER_WINNER
        if self.lose:
            return GameStateID.GAME_OVER

        for x in self.enemy_list:
            if not self.player_turn:
                x.base_distance = distance_in_tiles(pyasge.Point2D(x.sprite.x, x.sprite.y), pyasge.Point2D(1100, 128),
                                                    self.data)
                if not x.moved and not x.attacked:
                    x.get_state()

                for pc in self.player_list:
                    x.player_distance = distance_in_tiles(pyasge.Point2D(x.sprite.x, x.sprite.y),
                                                          pyasge.Point2D(pc.sprite.x, pc.sprite.y),
                                                          self.data)
                    if x.player_distance <= x.detection:
                        x.target = pyasge.Point2D(pc.sprite.x, pc.sprite.y)
                        x.destination = resolve(pyasge.Point2D(x.target.x, x.target.y), self.data, x, 0)
                        x.targeted_player = pc.id
                        if not x.moved and not x.attacked:
                            x.get_state()

                if x.hit_and_run and not x.locked:
                    x.start = pyasge.Point2D(x.sprite.x, x.sprite.y)
                    x.locked = True

                if x.attack_finish and x.hit_and_run and x.locked:
                    x.destination = resolve(x.start, self.data, x, 0)
                    if x.state != EnemyState.Run_Away:
                        x.animation_frame = 1
                    x.state = EnemyState.Run_Away
                    x.move(self.data)
                    if distance_in_tiles(pyasge.Point2D(x.sprite.x, x.sprite.y),
                                         x.start, self.data) < 1:
                        x.attack_finish = False
                        x.hit_and_run = False
                        x.state = EnemyState.Idle

                if not x.moved:
                    if x.state == EnemyState.Run_Towards:

                        x.player_distance = distance_in_tiles(pyasge.Point2D(x.sprite.x, x.sprite.y),
                                                              pyasge.Point2D(x.target.x, x.target.y),
                                                              self.data)
                        x.move(self.data)
                        if x.player_distance < 2:
                            x.moved = True
                            if x.attacked:
                                if x.state != EnemyState.Idle:
                                    x.animation_frame = 1
                                x.state = EnemyState.Idle
                            else:
                                if x.state != EnemyState.Attacking:
                                    x.animation_frame = 1
                                x.state = EnemyState.Attacking
                                x.data.audio_system.play_sound(x.sounds["attack"])

                    if x.state == EnemyState.Attacking:
                        if not x.attacked:
                            for pc in self.player_list:
                                if pc.id == x.targeted_player:
                                    pc.hp -= x.damage
                                    x.targeted_player = None
                        x.attacked = True

                    if x.state == EnemyState.Run_Away:
                        if x.base_distance < 2:
                            x.moved = True
                            x.state = EnemyState.Idle

            x.set_animation_state()
            x.run_animation(game_time)

        for pc in self.player_list:
            if self.player_turn:
                pc.move(self.data)

            pc.run_animation(game_time)

        # Code to end enemy turn
        if not self.player_turn:
            self.enemy_turn_over = True
            for x in self.enemy_list:
                if x.state != EnemyState.Idle:
                    self.enemy_turn_over = False
                elif x.hit_and_run and x.attacked:
                    self.enemy_turn_over = False

            if self.enemy_turn_over:
                for pc in self.player_list:
                    pc.attacked = False
                    pc.moved = False
                self.player_turn = True
                self.action_phase = False
                self.current_round.string = "Player Turn"
                # self.current_phase.string = "Planning phase "
                self.round += 1
                self.round_number.string = "Round: " + str(self.round)
                self.enemy_turn_over = False

        return GameStateID.GAMEPLAY

    def check_win_lose(self):
        for x in self.enemy_list:
            if x.health < 1:
                self.tombstones.append(Tombstone(x.sprite.x, x.sprite.y, "data/textures/skull.png", 0.03))
                self.enemy_list.remove(x)
                if len(self.enemy_list) < 1:
                    self.transition = True

        for pc in self.player_list:
            if pc.hp < 1:
                self.tombstones.append(Tombstone(pc.sprite.x, pc.sprite.y, "data/textures/Tombstone.png", 0.1))
                self.player_list.remove(pc)
                if len(self.player_list) < 1:
                    self.lose = True

    def update_camera(self):
        self.camera.translate(self.camera_vector.x,
                              self.camera_vector.y,
                              self.camera_zoom)
        view = [
            self.data.game_res[0] * 0.5 / self.camera.zoom,
            self.data.game_map.width * 48 - self.data.game_res[0] / self.camera.zoom,
            self.data.game_res[1] * 0.5 / self.camera.zoom,
            self.data.game_map.height * 38 - self.data.game_res[1] / self.camera.zoom
        ]
        self.camera.clamp(view)

    def render(self, game_time: pyasge.GameTime) -> None:
        """ Renders the game world and the UI """
        self.data.renderer.setViewport(pyasge.Viewport(0, 0, self.data.game_res[0], self.data.game_res[1]))
        self.data.renderer.setProjectionMatrix(self.camera.view)
        self.data.shaders["example"].uniform("rgb").set([1.0, 1.0, 0])
        self.data.game_map.render(self.data.renderer, game_time)
        self.render_ui()

        for x in self.tombstones:
            self.data.renderer.render(x.sprite)

        for x in self.enemy_list:
            x.render(self.data.renderer, game_time)

        for x in self.player_list:
            x.render(self.data.renderer, game_time)

        for x in self.grid_list:
            if x.visible:
                if x.selecting or x.reachable:
                    self.data.renderer.shader = self.shaders
                    x.render(self.data.renderer, game_time)
                else:
                    self.data.renderer.shader = None

                x.render(self.data.renderer, game_time)


        pass

    def render_ui(self) -> None:
        """ Render the UI elements and map to the whole window """
        # set a new view that covers the width and height of game
        camera_view = pyasge.CameraView(self.data.renderer.resolution_info.view)
        vp = self.data.renderer.resolution_info.viewport
        self.data.renderer.setProjectionMatrix(0, 0, vp.w, vp.h)
        self.data.renderer.render(self.next_round_instructions)
        self.data.renderer.render(self.current_round)
        self.data.renderer.render(self.round_number)
        self.data.renderer.render(self.player_health)
        self.data.renderer.render(self.quit_text)
        self.data.renderer.render(self.button)
        self.data.renderer.render(self.button1)
        self.data.renderer.render(self.button2)
        self.data.renderer.render(self.button3)
        self.data.renderer.render(self.button4)

        # this restores the original camera view
        self.data.renderer.setProjectionMatrix(camera_view)
