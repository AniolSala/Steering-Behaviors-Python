import pyglet
import pyglet.gl
from pyglet.window import mouse, key
from pyglet_arrow import Arrow
from numpy import array, ones, pi, random, linspace, sin, cos, angle, loadtxt, savetxt, exp
from numpy.linalg import norm
from pyglet_food import Food, Poison
import time


class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fps_display = pyglet.window.FPSDisplay(self)
        self.count = 1
        self.dnalist = []
        self.maxforce = .5
        self.showdna = 1

        self.maxfood = 15
        self.maxpoison = 40

        # Scale the dna[2:]
        self.scale = 1  # 200

        # Arrow list
        self.arrowlist = [Arrow(random.randint(
            self.width), random.randint(self.height)) for _ in range(4)]

        # Food list
        self.foodlist = [Food(random.randint(self.width), random.randint(
            self.height)) for i in range(self.maxfood * 2)]

        # Poison list
        self.poisonlist = [Poison(random.randint(self.width), random.randint(
            self.height)) for i in range(self.maxpoison)]

    def steerForce(self, arrow, target):
        if not target or not arrow:
            return array((0., 0.))

        desired = target.pos - arrow.center
        desired *= arrow.maxspeed / norm(desired)
        steering = desired - arrow.speed
        if norm(steering) > self.maxforce:
            steering *= self.maxforce / norm(steering)

        return steering

    def applyForce(self, force, arrow):
        if not arrow:
            return None
        arrow.accel += force

    def behaviors(self, arrow):
        '''We first look if the arrow has healt. If its health is 0,
        we remove it from arrowlist and we do not calculate the steering
        force'''

        if arrow.dead() is True:
            if len(self.dnalist) == 2:
                self.dnalist.remove(self.dnalist[0])
            self.dnalist.append(arrow.dna)
            self.arrowlist.remove(arrow)
            self.foodlist.append(Food(arrow.center[0], arrow.center[1]))
            return None

        closeF = arrow.seek(self.foodlist, self.scale * arrow.dna[2])
        closeP = arrow.seek(self.poisonlist, self.scale * arrow.dna[3])

        # If the closeF or closeP are very close, we eat them!
        disteat = arrow.maxspeed
        if closeF:
            if norm(closeF.pos - arrow.vertices.vertices[0:2]) < disteat\
                    or norm(closeF.pos - arrow.vertices.vertices[2:4]) < disteat\
                    or norm(closeF.pos - arrow.vertices.vertices[4:6]) < disteat\
                    or norm(closeF.pos - arrow.center) < disteat:
                arrow.feed(0.3)
                self.foodlist.remove(closeF)

        if closeP:
            if norm(closeP.pos - arrow.vertices.vertices[0:2]) < disteat\
                    or norm(closeP.pos - arrow.vertices.vertices[2:4]) < disteat\
                    or norm(closeP.pos - arrow.vertices.vertices[4:6]) < disteat\
                    or norm(closeP.pos - arrow.center) < disteat:
                arrow.feed(-0.75)
                self.poisonlist.remove(closeP)

        steerFood = self.steerForce(arrow, closeF)
        steerPois = self.steerForce(arrow, closeP)
        self.applyForce(steerFood * arrow.dna[0], arrow)
        self.applyForce(steerPois * arrow.dna[1], arrow)

    def clone(self, arrow):
        ''' Every time the function is called ther will
        be a x% of chance to clone the arrow. If the
        health of the arrow is less than 0.5, it can not
        clone.'''

        clone_rate = 0.00005 * (arrow.health - .3) / .7
        if random.rand() < clone_rate:
            self.arrowlist.append(
                Arrow(arrow.center[0], arrow.center[1], dna=arrow.dna))

    def boundaries(self, arrow):
        '''We want to keep the arrows in the world!'''

        # Distance from the walls that the arrow will start to spin
        d = 25

        desired = [None, None]

        if arrow.vertices.vertices[0] < d:
            desired = array((arrow.maxspeed, arrow.speed[1]))
        elif arrow.vertices.vertices[0] > self.width - d:
            desired = array((-arrow.maxspeed, arrow.speed[1]))

        if arrow.vertices.vertices[1] < d:
            desired = array((arrow.speed[0], arrow.maxspeed))
        elif arrow.vertices.vertices[1] > self.height - d:
            desired = array((arrow.speed[0], -arrow.maxspeed))

        # If it does not touch the bounds, nothing!
        if not desired[0]:
            return False

        desired *= arrow.maxspeed / norm(desired)
        steer = desired - arrow.speed
        if norm(steer) > self.maxforce:
            steer *= self.maxforce / norm(steer)

        self.applyForce(steer, arrow)

    def on_draw(self):
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA,
                              pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
        pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)

        for arrow in self.arrowlist:
            theta = arrow.getangle()
            pyglet.gl.glPushMatrix()
            pyglet.gl.glTranslatef(arrow.center[0], arrow.center[1], 0)
            pyglet.gl.glRotatef(theta, 0, 0, 1)

            # Draw the perceptions
            if self.showdna == -1:
                # Food perception:
                pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
                for ang in linspace(0, 2 * pi, 35):
                    pyglet.gl.glVertex2f(
                        self.scale * arrow.dna[2] * cos(ang), self.scale * arrow.dna[2] * sin(ang))
                    pyglet.gl.glColor4f(0, 1, 0, .6)
                pyglet.gl.glEnd()
                # Poison perception:
                pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
                for ang in linspace(0, 2 * pi, 35):
                    pyglet.gl.glVertex2f(
                        self.scale * arrow.dna[3] * cos(ang), self.scale * arrow.dna[3] * sin(ang))
                    pyglet.gl.glColor4f(1, 0, 0, .6)
                pyglet.gl.glEnd()

                # Drawing the food and poison atractions:
                pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
                pyglet.gl.glVertex2f(0, arrow.s / 2)
                pyglet.gl.glColor4f(0, 1., 0, 1)
                pyglet.gl.glVertex2f(0, arrow.s / 2 + 50 * arrow.dna[0])
                pyglet.gl.glColor4f(0, 1., 0, 1)
                pyglet.gl.glVertex2f(0, arrow.s / 2 + 2)
                pyglet.gl.glColor4f(0, 1., 0, 1)
                pyglet.gl.glEnd()

                pyglet.gl.glBegin(pyglet.gl.GL_LINE_STRIP)
                pyglet.gl.glVertex2f(0, arrow.s / 2)
                pyglet.gl.glColor4f(1, 0, 0, 1)
                pyglet.gl.glVertex2f(-1, arrow.s / 2 + 50 * arrow.dna[1])
                pyglet.gl.glColor4f(1, 0, 0, 1)
                pyglet.gl.glVertex2f(0, arrow.s / 2 + 2)
                pyglet.gl.glColor4f(1, 0, 0, 1)
                pyglet.gl.glEnd()

            # Checking bounds and behaviors
            self.boundaries(arrow)
            self.behaviors(arrow)

            # Drawing the arrow:
            pyglet.gl.glTranslatef(-arrow.center[0], -arrow.center[1], 0)
            arrow.vertices.draw(pyglet.gl.GL_TRIANGLES)

            pyglet.gl.glPopMatrix()

        # Finally we draw the food
        for food in self.foodlist:
            food.vertices.draw(pyglet.gl.GL_POLYGON)
        for poison in self.poisonlist:
            poison.vertices.draw(pyglet.gl.GL_POLYGON)

        # self.fps_display.draw()
        self.fps_display.set_fps(40)

    def mouse(self, x, y):
        if len(self.dnalist) != 0:
            self.arrowlist.append(
                Arrow(x, y,
                      dna=self.dnalist[random.randint(len(self.dnalist))]))
            print('We selected one of the best {} arrows.'.format(len(self.dnalist)))
        else:
            self.arrowlist.append(Arrow(x, y))

    def bestone(self):
        ''' Here we will save the best one '''

        if len(self.dnalist) != 0:
            savetxt('best_one.txt', self.dnalist[-1].reshape(1, 4))
            print(
                'The best arrow of the previous generation has been saved. Press o to load it')
        else:
            print('No arrows to save')

    def loadbest(self):
        ''' We load the best '''

        best = loadtxt('best_one.txt')
        if len(best) != 0:
            self.arrowlist = []
            self.arrowlist.append(
                Arrow(random.randint(self.width), random.randint(self.height), dna=best))
        else:
            print('No best arrows found')

    def writedna(self):
        ''' We will print the dna of the ten best
        arrows '''

        if len(self.dnalist) == 0:
            print('No arrow died yet')
            return False

        dna = array(self.dnalist)
        savetxt('bestdna.txt', dna)
        print('Lasts {} dna saved.'.format(len(self.dnalist)))

    def loaddna(self):
        '''Load the last dna saved'''

        loaddna = loadtxt('bestdna.txt')
        self.arrowlist = []
        if len(loaddna) == 0:
            print('No dna saved')
            return False

        for dna in loaddna:
            self.arrowlist.append(
                Arrow(random.randint(self.width), random.randint(self.height),
                      dna=dna))

        print('Loaded the last {} best arrows.'.format(len(loaddna)))

        self.dnalist = []
        for dna in loaddna:
            self.dnalist.append(dna)

    def printdna(self):
        print('The dan is:', self.dnalist)

    def update(self, dt):
        for arrow in self.arrowlist:
            arrow.update(dt)
            self.clone(arrow)

        # Adding new food and poison:
        if random.rand() < 0.12 and len(self.foodlist) <= self.maxfood:
            self.foodlist.append(
                Food(random.randint(self.width), random.randint(self.height)))
        if random.rand() < 0.1 and len(self.poisonlist) <= self.maxpoison:
            self.poisonlist.append(
                Poison(random.randint(self.width), random.randint(self.height)))

        # If all die, they take the adn of the lasts (see behavious func)
        if len(self.arrowlist) == 0:
            for dna in self.dnalist:
                self.arrowlist.append(Arrow(
                    random.randint(self.width), random.randint(self.height), dna=dna))

            self.count += 1


if __name__ == '__main__':
    world = MyWindow(width=800, height=600)
    pyglet.gl.glClearColor(.1, .1, .1, .1)
    world.on_draw()

    @world.event
    def on_mouse_press(x, y, button, modifiers):
        if button == mouse.LEFT:
            world.mouse(x, y)

    @world.event
    def on_key_press(symbol, modifiers):
        if symbol == key.D:
            world.showdna *= -1
        if symbol == key.P:
            world.printdna()
        if symbol == key.W:
            world.writedna()
        if symbol == key.L:
            world.loaddna()
        if symbol == key.B:
            world.bestone()
        if symbol == key.O:
            world.loadbest()

    pyglet.clock.schedule_interval(world.update, 1 / 40.)
    pyglet.app.run()
