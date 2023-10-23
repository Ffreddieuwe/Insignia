from functools import partial
from typing import Tuple

import numpy as np
import pyasge
import pytmx
from pytmx import TiledTileLayer


def other_library_loader(renderer: pyasge.Renderer, filename, colorkey, **kwargs):
    """Converts a tmx tile into a `pyasge.Tile`"""

    def extract_image(rect, flags):
        pyasge_tile = pyasge.Tile()
        pyasge_tile.texture = renderer.loadTexture(filename)
        pyasge_tile.texture.setMagFilter(pyasge.MagFilter.NEAREST)
        pyasge_tile.width = rect[2]
        pyasge_tile.height = rect[3]
        pyasge_tile.src_rect = rect
        pyasge_tile.visible = True

        # rotate the tile on both axis if needed
        if flags.flipped_diagonally:
            if flags.flipped_vertically:
                pyasge_tile.rotation = 4.71239
            else:
                pyasge_tile.rotation = 1.5708

        # or maybe just on a single axis
        else:
            if flags.flipped_horizontally:
                pyasge_tile.src_rect[0] += pyasge_tile.src_rect[2]
                pyasge_tile.src_rect[2] *= -1

            if flags.flipped_vertically:
                pyasge_tile.src_rect[1] += pyasge_tile.src_rect[3]
                pyasge_tile.src_rect[3] *= -1

        return pyasge_tile

    return extract_image


class GameMap:
    """
    The GameMap is the heart of soul of the game world.

    It's made up from tiles that are stored in 2D dimensional arrays.
    To improve performance when rendering the game, these tiles are
    pre-rendered on to a large texture and rendered in a single pass
    """

    def __init__(self, renderer: pyasge.Renderer, tmx_file: str) -> None:
        tmxdata = pytmx.TiledMap(tmx_file, partial(other_library_loader, renderer))

        # set the map's dimensions and tile sizes
        self.width = tmxdata.width
        self.height = tmxdata.height
        self.tile_size = [int(tmxdata.tilewidth * 2), int(tmxdata.tileheight * 2)]

        self.noGoArea = []
        for rect in tmxdata.layernames["NoGo"]:
            self.noGoArea.append([rect.x, rect.y, rect.width, rect.height])

        self.playerBase = []
        for rect in tmxdata.layernames["player base"]:
            self.playerBase.append([rect.x, rect.y, rect.width, rect.height])

        self.enemySpawn = []
        for obj in tmxdata.layernames["enemy spawns"]:
            self.enemySpawn.append((obj.x, obj.y))


        """create a new render target and sprite to store the render texture"""
        self.rt = pyasge.RenderTarget(
            renderer,
            self.width * self.tile_size[0], self.height * self.tile_size[1],
            pyasge.Texture.Format.RGBA, 1)

        self.map = []  # the tiled map
        self.costs = [[0 for i in range(tmxdata.width)] for j in range(tmxdata.height)]  # pathfinding costs
        for layer in tmxdata.visible_layers:
            if isinstance(layer, TiledTileLayer):

                tiles = [[None for i in range(layer.width)] for j in range(layer.height)]
                for x, y, tile in layer.tiles():
                    # use the tile image to create and position the map
                    tiles[y][x] = pyasge.Tile(tile)
                    tiles[y][x].width = self.tile_size[0]
                    tiles[y][x].height = self.tile_size[1]

                    # update the cost map with using the layer cost
                    self.costs[y][x] += layer.properties["cost"]

                self.map.append((layer.name, tiles))

        self.redraw = True

    def tile(self, world_space: pyasge.Point2D) -> Tuple[int, int]:
        """ Translate world space co-ordinates to tile location

        Given a position in the game world, this function will find the
        corresponding tile it resides in. This can be used to retrieve
        data from the cost map.

        Args:
            world_space (pygame.Vector2): The world-space position to convert
        """
        return int(world_space.x / self.tile_size[0]), int(world_space.y / self.tile_size[1])

    def world(self, tile_xy: Tuple[int, int]) -> pyasge.Point2D:
        """ Translate tile location to world space

        Given a tile location, this function will convert it to a
        position within the game world. It will always offset the
        position by the midpoint of the tile i.e. it's middle location

        Args:
            tile_xy (Tuple[int,int]):The tile location to convert
        """

        return pyasge.Point2D(
            ((tile_xy[0] + 1) * self.tile_size[0]) - (self.tile_size[0] * 0.5),
            ((tile_xy[1] + 1) * self.tile_size[1]) - (self.tile_size[1] * 0.5))

    def render(self, renderer: pyasge.Renderer, game_time: pyasge.GameTime) -> None:
        """ Renders the map and redraws it if needed """
        px_wide = self.width * self.tile_size[0]
        px_high = self.height * self.tile_size[1]

        if self.redraw:
            self.blit(renderer, px_high, px_wide)

        renderer.render(self.rt.buffers[0], [0, 0, px_wide, px_high], 0, 0, px_wide, px_high, 0)

    def blit(self, renderer, px_high, px_wide):
        """ Renders the game world in to a large single MSAA texture """

        # backup the current viewport and camera settings
        camera_view = np.array(renderer.resolution_info.view, copy=True)
        screen_viewport = pyasge.Viewport(renderer.resolution_info.viewport)

        # attach the offscreen texture and ensure whole map is framed
        renderer.setRenderTarget(self.rt)
        renderer.setProjectionMatrix(0, 0, px_wide, px_high)
        renderer.setViewport(pyasge.Viewport(0, 0, px_wide, px_high))

        # render the map
        for layer in self.map:
            for row_index, row in enumerate(layer[1]):
                for col_index, tile in enumerate(row):
                    if tile:
                        renderer.render(tile,
                                        col_index * self.tile_size[0],
                                        row_index * self.tile_size[1])

        # detach the offscreen texture and reset viewport and camera
        renderer.setRenderTarget(None)
        renderer.setViewport(screen_viewport)
        renderer.setProjectionMatrix(camera_view)

        # resolves the MSAA texture, ready for rendering
        self.rt.resolve()
        self.redraw = False
