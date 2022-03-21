from nethack_raph.Actions.Wait import Wait
from nethack_raph.Actions.Explore import Explore
from nethack_raph.Actions.Attack import Attack
from nethack_raph.Actions.RangeAttack import RangeAttack
from nethack_raph.Actions.OpenDoors import OpenDoors
from nethack_raph.Actions.Descend import Descend
from nethack_raph.Actions.Search import Search
from nethack_raph.Actions.FixStatus import FixStatus
from nethack_raph.Actions.RestoreHP import RestoreHP
from nethack_raph.Actions.Eat import Eat, EatFromInventory
from nethack_raph.Actions.Pray import Pray
from nethack_raph.Actions.PickUpStuff import PickUpStuff
from nethack_raph.Actions.Elbereth import Elbereth
from nethack_raph.Actions.UseItem import UseItem
from nethack_raph.Actions.Flash import Flash
from nethack_raph.Actions.EmergencyHeal import EmergencyHeal
from nethack_raph.Actions.FollowGuard import FollowGuard
from nethack_raph.Actions.Enhance import Enhance
from nethack_raph.Actions.RLTriggerAction import RLTriggerAction

from nethack_raph.Pathing import dijkstra_cpp, check_neighbours
from nethack_raph.myconstants import DUNGEON_WIDTH


class TestBrain:
    def __init__(self, kernel):
        self.kernel = kernel

        self.rl_actions = {
            'RangeAttack': RangeAttack(kernel),
            'Attack': Attack(kernel),
            'Wait': Wait(kernel),
            'Elbereth': Elbereth(kernel),
            'Pray': Pray(kernel),
        }

        self.actions = {
            'EmergencyHeal': EmergencyHeal(kernel),
            'Eat': Eat(kernel),
            'RestoreHP': RestoreHP(kernel),
            'EatFromInventory': EatFromInventory(kernel),
            'FollowGuard': FollowGuard(kernel),
            'UseItem': UseItem(kernel),
            'Enhance': Enhance(kernel),  # comment-out for minihack
            # 'Flash': Flash(kernel),
            'RLTriggerAction': RLTriggerAction(kernel),
            'Pray': Pray(kernel),
            'PickUpStuff': PickUpStuff(kernel),
            'FixStatus': FixStatus(kernel),
            # 'CheckTraps': CheckTraps(kernel),
            'Explore': Explore(kernel),
            'OpenDoors': OpenDoors(kernel),
            # 'Descend': Descend(kernel),
            'Search': Search(kernel),
            'Wait': Wait(kernel),
        }
        self.prev_action = -1
        self.prev_path = []

    def execute_next(self, level):
        # first-fit action selection
        for name, action in self.actions.items():
            # check if an action can be taken
            can_act, mask = action.can(level)
            if not can_act:
                action.after_search(mask, None)
                continue

            # local actions do not need pathfinding and return mask = None
            if mask is None:
                action.after_search(None, None)
                return action, None

            # actions that potentially require navigaton
            path = self.find_path(level, mask, name)
            action.after_search(mask, path)
            if path is None:
                self.kernel().log(f"Didn't find path for {name}")
                continue

            self.prev_action, self.prev_path = name, path
            self.kernel().log(f'found path length {len(path)} for {name}')
            return action, path

    def find_path(self, level, coords, action):
        hero = self.kernel().hero
        x, y = xy = hero.coords()  # hero.x, hero.y
        if coords[xy]:  # we are at the aim already
            return [xy]

        start = int(x * DUNGEON_WIDTH + y)
        flat_coords = coords.reshape(-1)

        use_prev_path = True
        if action != self.prev_action:  # doing not the same action as before
            use_prev_path = False
        elif len(self.prev_path) <= 3:  # less then 2 steps remaining
            use_prev_path = False
        elif self.prev_path[-2] != xy:  # didn't make a step to the right direction
            use_prev_path = False
        elif level.tiles.walk_cost[self.prev_path[-3]] != 1:  # Next step is not save
            use_prev_path = False
        elif check_neighbours(start, flat_coords):  # there is a goal nearby
            use_prev_path = False

        if use_prev_path:
            self.kernel().log(f'Use previous path')
            return self.prev_path[:-1]

        path = dijkstra_cpp(level.tiles.walk_cost, xy, coords, level.tiles.is_opened_door)

        return path
