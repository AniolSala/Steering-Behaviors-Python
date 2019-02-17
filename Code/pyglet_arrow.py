# from pyglet.gl import *
import pyglet
from numpy import array, angle, pi, random, inf, argsort, zeros
from numpy.linalg import norm


class Arrow():
    def __init__(self, posx, posy, dna=None * 4, color=[0, 1.0, 0, .4], *args, **kargs):
        self.s = 25.
        self._dna = dna

        # It will also have a healt:
        self.health = 1.
        self.alive = True

        # Arrow's physical features and drawing:
        self.maxspeed = 6
        self.speed = (array((random.rand(), random.rand()))
                      * 2 - 1.) * self.maxspeed
        self.accel = array((0., 0.))
        self.clist = color * 3
        self.center = array((posx, posy - self.s / 6))
        self.vlist = array([posx - self.s / 4, posy - self.s / 2,
                            posx + self.s / 4, posy - self.s / 2,
                            posx, posy + self.s / 2])
        self.vertices = pyglet.graphics.vertex_list(3, ('v2f', self.vlist),
                                                    ('c4f', self.clist))

    @property
    def _dna(self):
        return self.__dna

    @_dna.setter
    def _dna(self, new_dna):
        if new_dna is not None:
            # Modifying its DNA
            mutation_rate = .05
            self.__dna = new_dna + np.array([np.random.rand() if np.random.rand()
                                             < mutation_rate else 0 for _ in range(4)])
            print('New dna is:', self.__dna)
        else:
            # If the arrow has no dna create one
            sigma = .2
            self.__dna = sigma * np.random.randn(4)
            print('Creating new dna:', self.__dna)

    def seek(self, listel, perception):
        ''' Here the arrow will look for the closest
        element in the list '''

        if len(listel) == 0:
            return None

        closestE = None
        closestD = inf

        # We will look the vertex closest to the target
        for i in range(0, 5, 2):
            dlist = list(map(lambda thing: norm(
                thing.pos - self.vlist[i:i + 2]), listel))
            index = argsort(array(dlist))[0]
            if dlist[index] <= closestD and dlist[index] <= perception:
                closestD = dlist[index]
                closestE = index

        if closestE is None:
            return None

        return listel[closestE]

    def feed(self, nutrition):

        self.health += nutrition
        if self.health > 1.:
            self.health = 1.

    def dead(self):
        if self.health <= 0:
            return True
        return False

    def getangle(self):
        ''' The angle we will rotate the vehicle '''

        varrow = self.vlist[4:6] - (self.vlist[0:2] + self.vlist[2:4]) / 2.
        v1 = varrow[0] + varrow[1] * 1j
        v2 = self.speed[0] + self.speed[1] * 1j

        theta = (angle(v2) - angle(v1)) * 180. / pi
        # print(theta)
        return theta

    def update(self, dt):
        self.health -= 0.005

        # Set the color based on its healh label:
        if self.health < .5:
            red = 1.
            green = 2 * self.health
        else:
            red = 2 - 2 * self.health
            green = 1.
        self.vertices.colors = [red, green, 0, .6] * 3

        self.speed += self.accel
        if norm(self.speed) > self.maxspeed:
            self.speed *= self.maxspeed / norm(self.speed)
        self.center += self.speed
        for i in range(len(self.vlist)):
            self.vlist[i] += self.speed[i % 2]
        self.vertices.vertices = self.vlist
        self.accel *= 0.
