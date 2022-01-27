"""Room and Map"""
from copy import deepcopy

from .helper import DISPLAY as display
from .item import gen_items, get_item


class Map:
    def __init__(self, rooms, start, graph):
        self.rooms = gen_rooms(rooms)
        self.start = start
        self.graph = graph

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
    def __init__(self, name, desc, items):
        self.name = name
        self.desc = desc
        self.items = gen_items(items)

    def enter(self):
        """enter a room and display description text"""
        if enter_txt := self.desc.get("enter"):
            display.info(enter_txt)
        if look_txt := self.desc.get("look"):
            display.info(look_txt)
        return self

    def exit(self):
        """exit a room"""
        if exit_txt := self.desc.get("exit"):
            display.info(exit_txt)
        return self

    def find(self, name):
        """find item in the room"""
        return get_item(self.items, name)

    def look(self, syns, player, name):
        """look around room or at specific item"""
        if syns("around", name) is not None or name == "":
            if desc := self.desc.get("look"):
                display.info(desc)
            return None, []

        if item := self.find(name):
            _, desc, outcome = item.look(player)
            if desc:
                display.info(desc)
            return item, outcome
        return None, None

    def take(self, player, name):
        """take item from room"""
        new = None
        outcome = None
        if item := self.find(name):
            succ, desc, outcome = item.take(player)
            display.info(desc)
            if succ:
                new = deepcopy(item)
                if item.quantity > 1:
                    item.quantity -= 1
                    new.quantity = 1
                elif item.quantity == 1:
                    del self.items[item.name]
        return new, outcome

    def use(self, player, name):
        """use the item"""
        if item := self.find(name):
            desc, outcome = item.use(player)
            display.info(desc)
            return item, outcome
        return None, None
