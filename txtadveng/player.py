"""Player"""
from .helper import debug, response
from .item import get_item


class Player:
    def __init__(self, items=None, status=None):
        self.items = items or {}
        self.status = status or {}

    def find(self, name):
        """find item in inventory"""
        return get_item(self.items, name)

    def look(self, syns, name):
        """look at an item in the current room or inventory"""
        if (item_name := syns("inventory", name)) is not None:
            if item_name:
                if item := self.find(item_name):
                    response(f"You look at {item_name}")
                    if outcome := item.look(self):
                        debug(outcome)
                        return outcome
                response(f"Sorry, there is no '{item_name}' in your inventory.")
            elif items := self.items.keys():
                names = ", ".join(items)
                response(f"You look at the things you are carrying: {names}")
            else:
                response("You have no items right now.")
            return True
        return None

    def take(self, item):
        """take an item from the current room"""
        name = item.name
        if name in self.items:
            self.items[name].quantity += 1
        else:
            self.items[name] = item
