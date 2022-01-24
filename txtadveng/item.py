"""Item"""
import re

from .helper import response


class ItemVerb:
    def __init__(self, desc="", chance=1, require=None, succ=None, fail=None):
        self.desc = desc
        self.chance = chance
        self.require = require
        self.succ = succ or {}
        self.fail = fail or {}

    def __call__(self, player):
        if self.chance:
            return self.succ.get("desc"), self.succ.get("outcome")
        return self.fail.get("desc"), self.fail.get("outcome")


def gen_items(items):
    """generate items from given list of dicts"""
    gen = {}
    for name, item in items.items():
        if name in gen:
            gen[name].quantity += 1
        else:
            gen[name] = Item(name=name, **item)
    return gen


def get_item(items, name):
    """look for item that matches the given name"""
    for item in items.values():
        if _ := item.pattern.match(name):
            return item
    return None


class Item:
    def __init__(self, name, **kwargs):
        self.name = name
        names = "|".join([name] + kwargs.get("alt", []))
        self.pattern = re.compile(r"(?P<item>(" + names + r"))")
        self.quantity = kwargs.pop("quantity", 1)
        self.verbs = {
            "look": ItemVerb(**kwargs.pop("look", {})),
            "take": ItemVerb(**kwargs.pop("take", {})),
            "use": ItemVerb(**kwargs.pop("use", {})),
        }

        for key, val in kwargs.items():
            setattr(self, key, val)

    def __call__(self, player, act):
        if verb := self.verbs.get(act):
            desc, outcome = verb(player)
            response(desc)
            return outcome
        return None
