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
        return None


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
    def __init__(self, items=None, **kwargs):
        self.items = items or {}
        self.location = None
        self.status = {}

        for key, val in kwargs.items():
            setattr(self, key, val)

    def move(self, room):
        self.location = room
        self.location.enter()

    def look(self, name):
        if name == "self":
            names = ", ".join(self.items.keys())
            response(f"You look at the things you are carrying: {names}")
            return
        return self.location.look(name)

    def take(self, name):
        item, outcome = self.location.take(name)
        if item is None:
            response(f"No item named '{name}' to take")
            return None, None
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


class Item:
    def __init__(self, name, **kwargs):
        self.name = name
        names = "|".join([name] + kwargs.get("alt", []))
        self.pattern = re.compile(r"(?P<item>(" + names + r"))")
        self.verbs = {
            "look": None,
            "take": None,
            "use": None,
        }

        self.quantity = kwargs.get("quantity", 1)
        if "quantity" in kwargs:
            del kwargs["quantity"]

        if look := kwargs.get("look"):
            self.verbs["look"] = ItemVerb(**look)
            del kwargs["look"]
        if take := kwargs.get("take"):
            self.verbs["take"] = ItemVerb(**take)
            del kwargs["take"]
        if use := kwargs.get("use"):
            self.verbs["use"] = ItemVerb(**use)
            del kwargs["use"]

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

    def _get_item(self, name):
        for item in self.items.values():
            if match := item.pattern.match(name):
                return item
        return None

    def look(self, name):
        if item := self._get_item(name):
            response(f"You look at {name}")
            if outcome := item.do("look"):
                debug(outcome)
        else:
            response(f"Sorry, there is no item with the name '{name}' in the room.")

    def take(self, name):
        val = None
        outcome = None
        if item := self._get_item(name):
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


player = Player()
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
