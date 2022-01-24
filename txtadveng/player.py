"""Player"""
import re

from .helper import debug, response
from .item import get_item


class Player:
    def __init__(self, items=None, status=None, **kwargs):
        self.items = items or {}
        self.status = status or {}
        self.location = None
        names = "|".join(kwargs.pop("inventory", ["self"]))
        self.inventory = re.compile(r"(?P<verb>(" + names + r"))\s*(?P<nouns>.*)?")

        for key, val in kwargs.items():
            setattr(self, key, val)

    def move(self, room):
        """move to a new room"""
        self.location = room
        self.location.enter()

    def look(self, name):
        """look at an item in the current room or inventory"""
        if match := self.inventory.match(name):
            if item_name := match.group("nouns"):
                if item := get_item(self.items, item_name):
                    response(f"You look at {item_name}")
                    if outcome := item.do("look"):
                        debug(outcome)
                    return None
                response(f"Sorry, there is no '{item_name}' in your inventory.")
            elif items := self.items.keys():
                names = ", ".join(items)
                response(f"You look at the things you are carrying: {names}")
            else:
                response("You have no items right now.")
            return None
        return self.location.look(name)

    def take(self, name):
        """take an item from the current room"""
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
