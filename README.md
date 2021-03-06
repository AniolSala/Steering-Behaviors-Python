# Steering-Behaviors-Python
This [code](https://github.com/AniolSala/Steering-Behaviors-Python/tree/gh-pages/Code) is a Python implementation of this [video](https://www.youtube.com/watch?v=flxOkx0yLrY&t=)
using the Pyglet library. The main idea is that a bunge of entities (arrows) have to *eat* green targets (food) and avoid red targets (poison).

Each entitie has a *dna* that contains four qualities:

* Food attraction

* Posion attraction

* Food perception

* Poison perception

Food and poison attraction can be negative or positive, and the dna is initialized randomly for each arrow.

The *life* of each entity decreases some quantity each frame. If the entity hits a green target its life is slightly increased and if it hits a
red target it is slightly deacresed. When its life decreases to zero, the entitie desappears. When all entities of a generation desapear,
a new generation is created, inheriting the dna of the previous one. Each time the inheritence takes place, there is a tiny possibility that
some quality of the dna got slightly modified.

Not only this: an entitie can build a clone with its same dna. This probability is also very small, and so just the entities that live long enough could clone themselves and 
pass its dna to the clone. At the end of the day, just the entities with the best dna will survive and pass its genes to the next generation. 

