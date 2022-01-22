import readline
import shlex
import yaml
from pprint import pprint

with open("test.yml") as fp:
    config = yaml.load(fp, Loader=yaml.FullLoader)

pprint(config)


def get_input(prompt):
    return shlex.split(input(prompt))

# res = get_input("What is you're name?\n")
# print(res)


def run():
    while True:
        print(res := get_input("Question? "))
        if res[0] == "quit":
            break

run()
