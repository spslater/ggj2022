"""Room and Map"""
from copy import deepcopy

from .helper import debug, response
from .item import gen_items, get_item


class Map:
    def __init__(self, rooms, start, finish, graph, **kwargs):
        self.start = start
        self.finish = finish
        self.graph = graph
        self.rooms = gen_rooms(rooms)

        for key, val in kwargs.items():
            setattr(self, key, val)

    def get_room(self, name):
        """get the room with the given name in the map"""
        return self.rooms.get(name)

    def move(self, cur, direction):
        """move from current location in a specific direction"""
        room = self.graph.get(cur.name)
        dir_ = direction.lower()[0]
        name = room.get(dir_)
        return self.rooms.get(name)


def gen_rooms(rooms):
    """generate rooms from given dict"""
    gen = {}
    for name, room in rooms.items():
        if name in gen:
            val = gen[name]
            if not isinstance(val, list):
                gen[name] = [val]
            gen[name].append(val)
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
        """enter a room and display description text"""
        response(f"You have entered {self.name}.")
        response(self.desc)
        return self

    def look(self, name):
        """look around room or at specific item"""
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
        """take item from room"""
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
        """give item back to room?"""
        if item := get_item(self.items, name):
            name = item.name
            if name in self.items:
                self.items[name].append(item)
            else:
                self.items[name] = item
