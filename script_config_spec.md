# Script Config Spec Sheet
```yml
items:
  foo: &foo
    color: red
    weight: 1
  bar: &bar
    color: blue
    weight: 2

rooms:
  name: "test"
  description: |
    You are standing next to your bed.
    You see your desk and the garbage pile.
    To the East lies your roommate's area.
    To the South lies the door to the hallway (and showers).
  items:
    - *foo
    - *bar
```