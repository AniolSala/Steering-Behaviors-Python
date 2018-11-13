import pyglet
from numpy import array, pi, linspace, sin, cos


class Food():

    def __init__(self, x, y, color=[0, 1, 0, .7]):
        self.pos = array((x, y))
        self.r = 4
        N = 10
        self.clist = color * N
        self.vlist = []
        for angle in linspace(0, 2 * pi, N):
            self.vlist.append(self.r * cos(angle) + x)
            self.vlist.append(self.r * sin(angle) + y)

        self.vertices = pyglet.graphics.vertex_list(N, ('v2f', self.vlist),
                                                    ('c4f', self.clist))


class Poison():
    
    def __init__(self, x, y, color=[1, 0, 0, .7]):
        self.pos = array((x, y))
        self.r = 4
        N = 15
        self.clist = color * N
        self.vlist = []
        for angle in linspace(0, 2 * pi, N):
            self.vlist.append(self.r * cos(angle) + x)
            self.vlist.append(self.r * sin(angle) + y)

        self.vertices = pyglet.graphics.vertex_list(N, ('v2f', self.vlist),
                                                    ('c4f', self.clist))
