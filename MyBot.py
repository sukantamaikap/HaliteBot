import hlt
import logging
from collections import OrderedDict

game = hlt.Game("SM-V3")
logging.info("Starting my SM-V3 bot!")

itr = 0
while True:
    game_map = game.update_map()
    command_queue = []

    team_ships = game_map.get_me().all_ships()
    # logging.info("numbers of ships found : ", len(team_ships), "for iteration : ", itr)
    for ship in team_ships:

        if ship.docking_status != ship.DockingStatus.UNDOCKED:
            # logging.info("ship with id : ", ship.id, " is not undocked, skipping !!!!")
            continue

        entities_by_distance = OrderedDict(
            sorted(game_map.nearby_entities_by_distance(ship).items(), key=lambda t: t[0]))
        # find out empty planets
        closest_empty_planets = [entities_by_distance[distance][0] for distance in entities_by_distance
                                 if isinstance(entities_by_distance[distance][0], hlt.entity.Planet)
                                 and not entities_by_distance[distance][0].is_owned()]
        # find out empty ships
        closest_empty_ships = [entities_by_distance[distance][0] for distance in entities_by_distance
                               if isinstance(entities_by_distance[distance][0], hlt.entity.Ship)
                               and entities_by_distance[distance][0] not in team_ships]

        # logging.info("empty planets available for capture : ", len(closest_empty_planets))

        # as long as there are planets to capture, let's capture them
        if len(closest_empty_planets) > 0:
            target_planet = closest_empty_planets[0]
            if ship.can_dock(target_planet):
                # logging.info("docking planet : ", target_planet)
                command_queue.append(ship.dock(target_planet))
            else:
                navigate_command = ship.navigate(
                    ship.closest_point_to(target_planet),
                    game_map,
                    speed=int(hlt.constants.MAX_SPEED),
                    ignore_ships=False)

                if navigate_command:
                    command_queue.append(navigate_command)

        # now, as there are no planets left, attack the ships
        elif len(closest_empty_ships) > 0:
            target_ship = closest_empty_ships[0]
            navigate_command = ship.navigate(
                ship.closest_point_to(target_ship),
                game_map,
                speed=int(hlt.constants.MAX_SPEED),
                ignore_ships=False)

            if navigate_command:
                command_queue.append(navigate_command)
    game.send_command_queue(command_queue)
    # turn ends
# game ends
