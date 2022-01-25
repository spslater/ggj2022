import re

from .helper import response, debug
from .player import Player
from .room import Map


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

    def _look(self, name):
        # look at an item in the current room or inventory
        if self.player.look(self.syns, name) is not None:
            return None

        if (outcome := self.location.look(self.syns, self.player, name)) is not None:
            return outcome

        response(f"Sorry, there is no item with the name '{name}' in the room.")
        return None

    def _take(self, noun):
        item, outcome = self.location.take(self.player, noun)
        if item is not None:
            self.player.take(item)
        if outcome:
            debug(outcome)

    def _use(self, noun):
        debug(f"using at '{noun}'")

    def run(self):
        """run the adventure"""
        self._start()
        while True:
            res = input("Action? ")
            if self.syns("quit", res) is not None:
                self._quit()
                break
            elif (loc := self.syns("move", res)) is not None:
                self._move(loc)
            elif (name := self.syns("look", res)) is not None:
                self._look(name)
            elif (noun := self.syns("take", res)) is not None:
                self._take(noun)
            elif (noun := self.syns("use", res)) is not None:
                self._use(noun)
            else:
                response("sorry, i do know that command")
        self._end()
