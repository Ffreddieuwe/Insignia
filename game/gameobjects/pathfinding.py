import pyasge
from game.gamedata import GameData
import math


import heapq


def heuristic(node, goal):
    dx = node[0] - goal[0]
    dy = node[1] - goal[1]
    return math.sqrt(dx * dx + dy * dy)

def octile_distance(node, goal):
    dx = abs(node[0] - goal[0])
    dy = abs(node[1] - goal[1])
    return max(dx, dy) + (math.sqrt(2) - 1) * min(dx, dy)


def distance_in_tiles(start, goal, data: GameData):
    start_tile = data.game_map.tile(start)
    goal_tile = data.game_map.tile(goal)
    dx = abs(start_tile[0] - goal_tile[0])
    dy = abs(start_tile[1] - goal_tile[1])
    distance = dx + dy
    return distance

def distance_in_tiles_bytile(start, goal):
    dx = abs(start[0] - goal[0])
    dy = abs(goal[1] - start[1])
    distance = dx + dy
    return distance


def resolve(end_pos, data: GameData, start_pos, offset):
    start_tile = data.game_map.tile(pyasge.Point2D(start_pos.sprite.x, start_pos.sprite.y))
    goal_tile = data.game_map.tile(end_pos)

    # use these to make sure you don't go out of bounds when checking neighbours
    map_width = data.game_map.width

    # offset adjust the tiled based use for higher sprites
    map_height = data.game_map.height - offset
    start_cost = data.game_map.costs[start_tile[1]][start_tile[0]]
    goal_with_offset_y = goal_tile[1] - offset
    goal_cost = data.game_map.costs[goal_with_offset_y][goal_tile[0]]

    if not (0 <= start_tile[0] < map_width and 0 <= start_tile[1] < map_height):
        return []

    # if either the start or goal position is not walkable, return an empty path
    if start_cost > 1 or goal_cost > 1:
        return []

    frontier = []
    heapq.heappush(frontier, (0, start_tile))
    visited = set()
    previous_tile = {start_tile: None}
    cost_so_far = {start_tile: 0}

    while frontier:
        current_cost, current_tile = heapq.heappop(frontier)
        if current_tile == goal_tile:
            break

        visited.add(current_tile)
        neighbours = [(current_tile[0] - 1, current_tile[1]), (current_tile[0] + 1, current_tile[1]),
                      (current_tile[0], current_tile[1] - 1), (current_tile[0], current_tile[1] + 1)]

        for neighbour in neighbours:
            if neighbour not in visited:
                if 0 <= neighbour[0] < map_width and offset <= neighbour[1] < map_height:
                    neighbour_with_offset_y = (neighbour[1]+offset)
                    neighbor_cost = data.game_map.costs[neighbour_with_offset_y][neighbour[0]]
                    if neighbor_cost <= 1:
                        new_cost = cost_so_far[current_tile] + neighbor_cost
                        if neighbour not in cost_so_far or new_cost < cost_so_far[neighbour]:
                            new_cost = cost_so_far[current_tile] + neighbor_cost
                            priority = new_cost + distance_in_tiles_bytile(goal_tile, neighbour)
                            if neighbour not in cost_so_far or new_cost < cost_so_far[neighbour]:
                                cost_so_far[neighbour] = new_cost
                                heapq.heappush(frontier, (priority, neighbour))
                                previous_tile[neighbour] = current_tile

    path = []
    current_tile = goal_tile
    while current_tile != start_tile:
        path.insert(0, data.game_map.world(current_tile))
        current_tile = previous_tile[current_tile]

    return path


"""
def resolve1(xy: pyasge.Point2D, data: GameData, player):

    Resolves the path needed to get to the destination point.
    Making use of the cost map, a suitable search algorithm should
    be used to create a series of tiles that the ship may pass
    through. These tiles should then be returned as a series of
    positions in world space.
    :param xy: The destination for the ship
    :param data: The game data, needed for access to the game map
    :param player: the moving object
    :return: list[pyasge.Point2D]


    # convert point to tile location
    player_location = data.game_map.tile(pyasge.Point2D(player.sprite.x, player.sprite.y))
    tile_loc = data.game_map.tile(xy)

    map_width = data.game_map.width
    map_height = data.game_map.height

    if not (0 <= tile_loc[0] < map_width and 0 <= tile_loc[1] < map_height):
        return []

    tile_cost = data.game_map.costs[tile_loc[1]][tile_loc[0]]
    path = []

    if tile_cost < 100:
        came_from = dict()
        came_from[player_location] = None

        tiles_to_visit = [player_location]

        while len(tiles_to_visit) > 0:

            current_tile = tiles_to_visit[0]
            tiles_to_visit.pop(0)

            if current_tile == tile_loc:
                break

            neighbors = [(current_tile[0]+1, current_tile[1]),
                         (current_tile[0]-1, current_tile[1]),
                         (current_tile[0], current_tile[1]+1),
                         (current_tile[0], current_tile[1]-1)]
            for neighbor in neighbors:

                if neighbor[0] >= map_width or neighbor[0] < 0:
                    neighbors.remove(neighbor)
                elif neighbor[1] >= map_height or neighbor[1] < 0:
                    neighbors.remove(neighbor)
                elif (data.game_map.costs[neighbor[1]][neighbor[0]]) > 1:
                    neighbors.remove(neighbor)

            for next_tile in neighbors:
                if next_tile not in came_from:
                    tiles_to_visit.append(next_tile)
                    came_from[next_tile] = current_tile

        current_tile = tile_loc

        while current_tile != player_location:
            path.insert(0, data.game_map.world(current_tile))
            current_tile = came_from[current_tile]




        # return a list of tile positions to follows
    return path
"""