# from pyglet.gl import *
import pyglet
from numpy import array, angle, pi, random, inf, argsort, zeros
from numpy.linalg import norm


class Arrow():
    def __init__(self, posx, posy, dna=[None] * 4, color=[0, 1.0, 0, .4], *args, **kargs):
        self.s = 25.
        # To set the dna:
        if not dna[0]:
            self.dna = zeros(4)
            # Food / Poison weight (random numbert between -2 and 2):
            self.dna[:2] = random.rand(2) * 4. - 2.
            # Food / Poison perception:
            self.dna[2:] = random.rand(2) * (120. - self.s / 2) + self.s / 2

        else:
            # Mutation! (we call mr the mutation rate)
            self.dna = dna
            self.mr = .05    # Mutation rate

            self.dna[0] = dna[0]
            if random.rand() < self.mr:
                self.dna[0] += random.rand() * 0.5 - 0.5
            self.dna[1] = dna[1]
            if random.rand() < self.mr:
                self.dna[1] += random.rand() * 0.5 - 0.5
            self.dna[2] = dna[2]
            if random.rand() < self.mr:
                self.dna[2] += random.rand() * 20. - 10.
            self.dna[3] = dna[3]
            if random.rand() < self.mr:
                self.dna[3] += random.rand() * 20. - 10.

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
