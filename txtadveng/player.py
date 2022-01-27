"""Player"""
from .helper import DISPLAY as display
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
                    display.info("You look at %s", item_name)
                    if outcome := item.look(self):
                        display.debug("%s", outcome)
                        return outcome
                display.info("Sorry, there is no '%s' in your inventory.", item_name)
            elif items := self.items.keys():
                names = ", ".join(items)
                display.info("You look at the things you are carrying: %s", names)
            else:
                display.info("You have no items right now.")
            return True
        return None

    def take(self, item):
        """take an item from the current room"""
        name = item.name
        if name in self.items:
            self.items[name].quantity += 1
        else:
            self.items[name] = item

    def use(self, name):
        """use an item"""
        if item := self.find(name):
            desc, outcome = item.use(self)
            display.info(desc)
            return item, outcome
        return None, None
