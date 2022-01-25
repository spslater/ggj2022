"""Item"""
import re


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


class ItemVerb:
    def __init__(self, require=None, chance=1, succ=None, fail=None):
        self.require = require
        self.chance = chance
        self.succ = succ or {}
        self.fail = fail or {}

    def __call__(self, player):
        if self._require(player) and self.chance:
            return True, self.succ.get("desc"), self.succ.get("outcome", [])
        return False, self.fail.get("desc"), self.fail.get("outcome", [])

    def _require(self, player):
        if self.require is not None:
            check = self.require[0]
            if check == "status":
                stat, val = self.require[1:3]
                if val == player.status.get(stat):
                    return True
            return False
        return True


class Item:
    def __init__(self, name, **kwargs):
        self.name = name
        names = "|".join([name] + kwargs.pop("alt", []))
        self.pattern = re.compile(r"(?P<item>(" + names + r"))")
        self.quantity = kwargs.pop("quantity", 1)
        self.status = kwargs.pop("status", {})
        self.verbs = {
            "look": ItemVerb(**kwargs.pop("look", {})),
            "take": ItemVerb(**kwargs.pop("take", {})),
            "use": ItemVerb(**kwargs.pop("use", {})),
        }

    def look(self, player):
        """look at item"""
        return self.verbs["look"](player)

    def take(self, player):
        """take item"""
        succ, desc, outcome = self.verbs["take"](player)
        if succ:
            if outcome is None:
                outcome = []
            if "take" not in outcome:
                outcome += ["take"]
            return True, desc, outcome
        return False, desc, outcome

    def use(self, player):
        """use item"""
        return self.verbs["use"](player)
