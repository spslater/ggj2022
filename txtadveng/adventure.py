import re
from enum import Enum, auto

from .helper import response, debug, Display
from .player import Player
from .room import Map

display = Display()

class Similar:
    def __init__(self, primary, synonyms):
        self.name = primary
        syns = "|".join(sorted([primary] + synonyms, reverse=True))
        self.pattern = re.compile(r"(" + syns + r")\s*(?P<token>.*)?")

    def __call__(self, string):
        if match := self.pattern.match(string):
            return match.group("token")
        return None


class Synonyms:
    def __init__(self, config):
        self.config = config
        for primary, synonyms in self.config.items():
            setattr(self, primary, Similar(primary, synonyms))

    def __call__(self, primary, string):
        if similar := getattr(self, primary, None):
            return similar(string)
        return None


class Outcome(Enum):
    NONE = auto()
    END = auto()
    STATUS = auto()
    VISIBLE = auto()


class Adventure:
    def __init__(self, config):
        self.config = config

        self.player = Player(**self.config["player"])
        self.worldmap = Map(
            self.config["rooms"],
            self.config["start"],
            self.config["map"],
        )
        self.syns = Synonyms(self.config["synonyms"])
        self.location = self.worldmap.get_room(self.worldmap.start)

    def _start(self):
        if intro := self.config.get("intro"):
            response(intro)
        if look := self.location.desc.get("look"):
            response(look)

    def _end(self):
        if outro := self.config.get("outro"):
            response(outro)

    @staticmethod
    def _quit():
        response("thanks for playing!")

    def _move(self, loc):
        if room := self.worldmap.move(self.location, loc):
            self.location.exit()
            self.location = room.enter()
        else:
            response("no room in that direction")
        return Outcome.NONE

    def _look(self, name):
        # look at an item in the current room or inventory
        if self.player.look(self.syns, name) is not None:
            return Outcome.NONE

        item, outcome = self.location.look(self.syns, self.player, name)
        if outcome is not None:
            return self._outcome(item, outcome)

        response(f"Sorry, there is no item with the name '{name}' in the room.")
        return Outcome.NONE

    def _take(self, noun):
        item, outcome = self.location.take(self.player, noun)
        if item is None:
            return None, None
        self.player.take(item)
        return self._outcome(item, outcome)

    def _use(self, noun):
        item, outcome = self.location.use(self.player, noun)
        if item is None:
            item, outcome = self.player.use(noun)

        if item is None:
            response(f"Sorry, there is no item with the name '{noun}' to use.")
            return

        return self._outcome(item, outcome)

    def _outcome(self, item, outcome):
        """execute the outcome associated with item"""
        debug(item, outcome)
        if not outcome:
            return Outcome.NONE
        if "status" == outcome[0]:
            self.player.status[outcome[1]] = outcome[2]
            return Outcome.NONE
        if "reveal" == outcome[0]:
            item.status[outcome[1]] = True
            return Outcome.NONE
        if "end" == outcome[0]:
            return Outcome.END
        return Outcome.NONE


    def run(self):
        """run the adventure"""
        self._start()
        outcome = Outcome.NONE
        while True:
            res = input("Action? ")
            if self.syns("quit", res) is not None:
                self._quit()
                break
            if (loc := self.syns("move", res)) is not None:
                outcome = self._move(loc)
            elif (name := self.syns("look", res)) is not None:
                outcome = self._look(name)
            elif (noun := self.syns("take", res)) is not None:
                outcome = self._take(noun)
            elif (noun := self.syns("use", res)) is not None:
                outcome = self._use(noun)
            elif (noun := self.syns("status", res)) is not None:
                debug(self.player.status)
            else:
                response("sorry, i do know that command")
            if outcome is Outcome.END:
                self._quit()
                break
        self._end()
