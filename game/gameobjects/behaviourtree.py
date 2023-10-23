from enum import Enum


class EnemyState(Enum):
    Idle = 1
    Attacking = 2
    Run_Towards = 3
    Run_Away = 4
    Take_Damage = 5
    Death = 6


def goblin_bt(goblin):
    if goblin.detection > goblin.player_distance:
        if goblin.health > 5:
            #Sequence Run to Player - Attack - Run away
            goblin.state = EnemyState.Run_Towards
            return
        else:
            if goblin.health > 2:
                if goblin.player_distance < 2:
                    goblin.state = EnemyState.Attacking
                    return
                else:
                    goblin.state = EnemyState.Idle
                    return
            else:
                if goblin.player_distance < 2:
                    goblin.state = EnemyState.Attacking
                    return
                else:
                    goblin.state = EnemyState.Idle
                    return
    else:
        goblin.state = EnemyState.Idle
        return


def mushroom_bt(mushroom):
    if mushroom.detection > mushroom.player_distance:
        if mushroom.player_distance < 3:
            mushroom.state = EnemyState.Attacking
            return
        else:
            if mushroom.health > 10:
                mushroom.attacked = True
                mushroom.state = EnemyState.Run_Towards
                return
            else:
                mushroom.state = EnemyState.Idle
                return
    else:
        mushroom.state = EnemyState.Idle
        return


def skeleton_bt(skeleton):
    if skeleton.detection > skeleton.player_distance:
        if skeleton.health > 7:
            # Sequence Run to Player - Attack
            skeleton.state = EnemyState.Run_Towards
            return
        else:
            if skeleton.player_distance < 2:
                skeleton.state = EnemyState.Attacking
                return
            else:
                skeleton.state = EnemyState.Idle
                return
    else:
        skeleton.state = EnemyState.Idle
        return


def eye_bt(eye):
    if eye.detection > eye.player_distance:
        if eye.health > 4:
            # Sequence Run to Player - Attack
            eye.state = EnemyState.Run_Towards
            return
        else:
            if eye.player_distance < 2:
                eye.state = EnemyState.Attacking
                return
            else:
                eye.state = EnemyState.Idle
                return
    else:
        eye.state = EnemyState.Idle
        return


