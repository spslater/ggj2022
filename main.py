import re
import readline
import shlex
import yaml

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

    def take(self, name):
        item = self.location.give(name)
        if item is None:
            response(f"No item named '{name}' to take")
            return
        name = item.name
        if name in self.items:
            val = self.items[name]
            if not isinstance(val, list):
                self.items[name] = [val]
            self.items[name].append(item)
        else:
            self.items[name] = item


def gen_items(items):
    gen = {}
    for name, item in items.items():
        if name in gen:
            val = gen[name]
            if not isinstance(val, list):
                gen[name] = [val]
            gen[name].append(item)
        else:
            gen[name] = Item(name=name, **item)
    return gen


class Item:
    def __init__(self, name, **kwargs):
        self.name = name
        names = "|".join([name] + kwargs.get("alt", []))
        self.pattern = re.compile(r"(?P<item>("+names+r"))")

        for key, val in kwargs.items():
            setattr(self, key, val)

    def look(self):
        response(self.desc)

    def use(self):
        pass

    def consume(self):
        pass


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
        for item in self.items.values():
            if match := item.pattern.match(name):
                response(f"You look at {name}")
                item.look()
                return
        response(f"Sorry, there is no item with the name '{name}' in the room.")

    def take(self, item):
        name = item.name
        if name in self.items:
            val = self.items[name]
            if not isinstance(val, list):
                self.items[name] = [val]
            self.items[name].append(item)
        else:
            self.items[name] = item

    def give(self, name):
        if name not in self.items:
            return None

        val = self.items[name]
        if not isinstance(val, list):
            del self.items[name]
            return val

        val = self.items[name].pop()
        return val


player = Player()
worldmap = Map(config["rooms"], config["start"], config["finish"], config["map"])

player.location = worldmap.get_room(worldmap.start)

acts = Action(config["verbs"])


def move(noun):
    room = worldmap.move(player.location, noun)
    if room:
        player.move(room)
    else:
        response("no room in that direction")


def look(noun):
    room = player.location
    room.look(noun)


def use(noun):
    debug(f"useing at '{noun}'")


def take(noun):
    debug(f"taking at '{noun}'")


def run():
    while True:
        verb, noun = acts.do("Action? ")
        if verb is None:
            response("sorry, i do know that command")
            continue

        if verb == "quit":
            response("thanks for playing!")
            break

        if verb == "move":
            move(noun)
            continue

        if verb == "look":
            look(noun)
            continue

        if verb == "use":
            use(noun)
            continue

        if verb == "take":
            take(noun)
            continue


run()
