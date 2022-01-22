import readline
import shlex
import yaml
from pprint import pprint

with open("test.yml") as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)


def act(prompt):
    return shlex.split(input(prompt))


class Map:
    def __init__(self, rooms, start, finish, graph):
        self.start = start
        self.finish = finish
        self.graph = graph
        self.rooms = gen_rooms(rooms)

    def get_room(self, name):
        return self.rooms.get(name)

    def move(self, cur, direction):
        room = self.graph.get(cur.name)
        dir_ = direction.lower()[0]
        name = room.get(dir_)
        return self.rooms.get(name)


class Player:
    def __init__(self, items=None):
        self.items = items or {}
        self.location = None

    def move(self, room):
        self.location = room
        self.location.enter()

    def take(self, name):
        item = self.location.give(name)
        if item is None:
            print(f"No item named '{name}' to take")
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
    def __init__(self, name, color, weight, desc):
        self.name = name
        self.color = color
        self.weight = weight
        self.desc = desc

    def look(self):
        print(self.desc)

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
    def __init__(self, name, desc, items):
        self.name = name
        self.desc = desc
        self.items = gen_items(items)

    def enter(self):
        print(f"You have entered {self.name}.")
        print(self.desc)
        return self

    def look(self, name):
        if name in self.items:
            print(f"You look at {name}")
            self.items[name].look()
        else:
            print("Sorry, there is no item with that name in the room.")

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


def run():
    while True:
        res = act("Direction? ")
        if res[0] in ("quit", "q"):
            break
        room = worldmap.move(player.location, res[0])
        if room:
            player.move(room)
        else:
            print("no room in that direction")


run()
