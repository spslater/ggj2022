# Global Game Jam 2022
* plug and play
* script parser
* action parser [verb] [noun] (check if noun is in range)
* keep track of location
* inventory
* store history

## actions
Make sure that each scripted command only works if you're in the correct room!
* look at things
  * probably with several synonyms that all work.
  * Look, look at, examine, inspect, view, etc.
  * Typing "look" by itself repeats the initial description of the room.

* use things
  * probably "use"
  * Sometimes this might prompt the player to say what to use it with
    * like "Use X with what?"
    * to prompt a "Use X with Y" syntax.
    * maybe to use two items together do a "combine"

* pick up things
  * probably with synonyms pick up, take, grab, etc
  * "inventory" command to show what they currently are holding.
  * you are already holding the {X} if item is already in inventory.
* move
  * with synonyms go, move, walk etc.

## classes
* room (map)
* things, items, objects 
* actions
* self
* plot