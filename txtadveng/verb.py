"""Verb and Action"""
import re


class Act:
    def __init__(self, primary, synonyms, **kwargs):
        self.name = primary
        acts = "|".join([primary] + synonyms)
        self.pattern = re.compile(r"(?P<verb>(" + acts + r"))\s*(?P<noun>.*)?")

        for key, val in kwargs.items():
            setattr(self, key, val)


class Action:
    def __init__(self, verbs, **kwargs):
        self.verbs = {}
        for verb, synonyms in verbs.items():
            self.verbs[verb] = Act(verb, synonyms)

        for key, val in kwargs.items():
            setattr(self, key, val)

    def do(self, prompt):
        """perfrom action"""
        res = input(prompt)
        for verb in self.verbs.values():
            if match := verb.pattern.match(res):
                return verb.name, match.group("noun")
        return None, None
