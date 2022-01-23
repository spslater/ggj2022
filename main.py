import re
import readline
import shlex
import yaml
from copy import deepcopy

with open("test.yml") as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)


def response(*args, **kwargs):
    print("> ", *args, **kwargs)


def debug(*args, **kwargs):
    print("? ", *args, **kwargs)


class Act:
    def __init__(self, primary, synonyms, **kwargs):
        self.name = primary
        acts = "|".join([primary] + synonyms)
        self.pattern = re.compile(r"(?P<verb>(" + acts + r"))\s*(?P<noun>.*)?")

        for key, val in kwargs.items():
            setattr(self, key, val)


class Action:
    def __init__(self, verbs, **kwargs):
        self.verbs = {}
        for verb, synonyms in verbs.items():
            self.verbs[verb] = Act(verb, synonyms)

        for key, val in kwargs.items():
            setattr(self, key, val)

    def do(self, prompt):
        res = input(prompt)
        for verb in self.verbs.values():
            if match := verb.pattern.match(res):
                return verb.name, match.group("noun")
        return None, None


class Map:
    def __init__(self, rooms, start, finish, graph, **kwargs):
        self.start = start
        self.finish = finish
        self.graph = graph
        self.rooms = gen_rooms(rooms)

        for key, val in kwargs.items():
            setattr(self, key, val)

    def get_room(self, name):
        return self.rooms.get(name)

    def move(self, cur, direction):
        room = self.graph.get(cur.name)
        dir_ = direction.lower()[0]
        name = room.get(dir_)
        return self.rooms.get(name)


class Player:
    def __init__(self, items=None, status=None, **kwargs):
        self.items = items or {}
        self.status = status or {}
        self.location = None
        names = "|".join(kwargs.pop("inventory", ["self"]))
        self.inventory = re.compile(r"(?P<verb>("+names+r"))\s*(?P<nouns>.*)?")

        for key, val in kwargs.items():
            setattr(self, key, val)

    def move(self, room):
        self.location = room
        self.location.enter()

    def look(self, name):
        if match := self.inventory.match(name):
            if item_name := match.group("nouns"):
                if item := get_item(self.items, item_name):
                    response(f"You look at {item_name}")
                    if outcome := item.do("look"):
                        debug(outcome)
                    return
                response(f"Sorry, there is no '{item_name}' in your inventory.")
            elif items := self.items.keys():
                names = ", ".join(items)
                response(f"You look at the things you are carrying: {names}")
            else:
                response(f"You have no items right now.")
            return
        return self.location.look(name)

    def take(self, name):
        item, outcome = self.location.take(name)
        if item is None:
            response(f"No item named '{name}' to take")
            return None, None
        if outcome == "take":
            name = item.name
            if name in self.items:
                self.items[name].quantity += 1
            else:
                self.items[name] = item
        return item, outcome


class ItemVerb:
    def __init__(
        self,
        desc="",
        chance=1,
        require=None,
        succ=None,
        fail=None,
        outcome=None,
    ):
        self.desc = desc
        self.chanse = chance
        self.require = require
        self.succ = succ or {}
        self.fail = fail or {}

    def do(self):
        if self.chanse:
            return self.succ.get("desc"), self.succ.get("outcome")
        return self.fail.get("desc"), self.fail.get("outcome")


def gen_items(items):
    gen = {}
    for name, item in items.items():
        if name in gen:
            gen[name].quantity += 1
        else:
            gen[name] = Item(name=name, **item)
    return gen


def get_item(items, name):
    for item in items.values():
        if match := item.pattern.match(name):
            return item
    return None


class Item:
    def __init__(self, name, **kwargs):
        self.name = name
        names = "|".join([name] + kwargs.get("alt", []))
        self.pattern = re.compile(r"(?P<item>(" + names + r"))")
        self.verbs = {
            "look": ItemVerb(**kwargs.pop("look", {})),
            "take": ItemVerb(**kwargs.pop("take", {})),
            "use": ItemVerb(**kwargs.pop("use", {})),
        }

        self.quantity = kwargs.pop("quantity", 1)

        # if look := kwargs.pop("look", None):
        #     self.verbs["look"] = ItemVerb(**look)
        # if take := kwargs.pop("take", None):
        #     self.verbs["take"] = ItemVerb(**take)
        # if use := kwargs.pop("use", None):
        #     self.verbs["use"] = ItemVerb(**use)

        for key, val in kwargs.items():
            setattr(self, key, val)

    def do(self, act):
        if verb := self.verbs.get(act):
            desc, outcome = verb.do()
            response(desc)
            return outcome
        return None


def gen_rooms(rooms):
    gen = {}
    for name, room in rooms.items():
        if name in gen:
            val = gen[name]
            if not isinstance(val, list):
                gen[name] = [val]
            gen[name].append(item)
        else:
            gen[name] = Room(name=name, **room)
    return gen


class Room:
    def __init__(self, name, desc, items, **kwargs):
        self.name = name
        self.desc = desc
        self.items = gen_items(items)

        for key, val in kwargs.items():
            setattr(self, key, val)

    def enter(self):
        response(f"You have entered {self.name}.")
        response(self.desc)
        return self


    def look(self, name):
        if name == "around":
            response("You look around the room again.")
            response(self.desc)
            return

        if item := get_item(self.items, name):
            response(f"You look at {name}")
            if outcome := item.do("look"):
                debug(outcome)
            return
        response(f"Sorry, there is no item with the name '{name}' in the room.")
        return

    def take(self, name):
        val = None
        outcome = None
        if item := get_item(self.items, name):
            outcome = item.do("take")
            val = deepcopy(item)
            if item.quantity > 1:
                item.quantity -= 1
                val.quantity = 1
            elif item.quantity == 1:
                del self.items[item.name]
        return val, outcome

    def give(self, name):
        name = item.name
        if name in self.items:
            self.items[name].append(item)
        else:
            self.items[name] = item


player = Player(**config["player"])
worldmap = Map(
    config["rooms"],
    config["start"],
    config["finish"],
    config["map"],
)
acts = Action(config["verbs"])
player.location = worldmap.get_room(worldmap.start)


def run():
    response(config["intro"])
    while True:
        verb, noun = acts.do("Action? ")
        if verb is None:
            response("sorry, i do know that command")
            continue

        if verb == "quit":
            response("thanks for playing!")
            break

        if verb == "move":
            room = worldmap.move(player.location, noun)
            if room:
                player.move(room)
            else:
                response("no room in that direction")
            continue

        if verb == "look":
            player.look(noun)
            continue

        if verb == "take":
            item, outcome = player.take(noun)
            continue

        if verb == "use":
            debug(f"using at '{noun}'")
            continue


run()
