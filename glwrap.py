#! /usr/bin/env python3

from functools import wraps
from multiprocessing import Process
from threading import Thread
from time import time

from OpenGL.GL import *
# from OpenGL.arrays import vbo
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

from vector import vector


class GlObject:
    vertices = ((0.45, 0.45, -0.45),
                (-0.45, 0.45, -0.45),
                (-0.45, 0.45, 0.45),
                (0.45, 0.45, 0.45),
                (0.45, -0.45, 0.45),
                (-0.45, -0.45, 0.45),
                (-0.45, -0.45, -0.45),
                (0.45, -0.45, -0.45))
    corners = ((1.0, 1.0),
               (0.0, 1.0),
               (0.0, 0.0),
               (1.0, 0.0))
    surfaces = ((0, 1, 2, 3),
                # (7, 6, 5, 4),
                # (3, 2, 5, 4),
                # (1, 0, 7, 6),
                # (1, 2, 5, 6),
                # (3, 0, 7, 4),
                )

    def __init__(self, centre: vector, texid: int):
        self.position = vector(centre)
        self.texture = texid

    def draw(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        for vertex_ids in GlObject.surfaces:
            for tex_coord, vertex in zip(GlObject.corners, vertex_ids):
                glTexCoord2f(*tex_coord)
                glVertex3f(*self.vertices[vertex])
        glEnd()

    @property
    def position(self):
        return self.pos

    @position.setter
    def position(self, v: vector):
        x, y, z = v
        self.pos = vector([x, z, y])
        self.vertices = tuple(tuple(map(sum, zip(vertex, self.pos)))
                              for vertex in GlObject.vertices)


@wraps
class Memoize:
    def __init__(self, f):
        self.f = f
        self.memo = {}

    def __call__(self, *args, **kwargs):
        if args not in self.memo:
            self.memo[args] = self.f(*args, **kwargs)
        return self.memo[args]


def renderer(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        self.fps, dtime = time(), time() - self.fps
        glutSetWindowTitle("FPS: %02d" % (1 / dtime,))
        # glUseProgram(SHADER)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(*self.camera_offset,
                  *(0.0, 0.0, 0.0),
                  *(0.0, 1.0, 0.0))
        glRotatef(self.camera_rot[1], -1.0, 0.0, 0.0)
        glRotatef(self.camera_rot[0], 0.0, 1.0, 0.0)
        glTranslatef(*(self.camera_pos))
        func(self, *args, **kwargs)
        glutSwapBuffers()
    return wrapper


def multiprocess(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        process = Process(target=func, args=args, kwargs=kwargs)
        process.start()
        return process
    return wrapper


def thread(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        process = Thread(target=func, args=args, kwargs=kwargs)
        process.start()
        return process
    return wrapper


def timeit(method):
    from time import time

    def timed(*args, **kw):
        ts = time()
        result = method(*args, **kw)
        te = time()
        print(te - ts)
        return result
    return timed


class GlManager:

    def __init__(self, pipe, width: int, height: int, fov=45.0, depth=50.0):
        self.pipe = pipe
        self.fps = time()
        self.camera_pos = vector([0.0, 0.0, 0.0])
        self.camera_offset = vector([0, 10.0, -10.0])
        self.camera_rot = [180.0, 0.0]
        self.textures = {}
        self.keypresses = {}
        self.renders = []
        # OpenGL stuff
        self.width, self.height = width, height
        self.fov, self.depth = fov, depth

    def gl_init(self):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(200, 200)
        glutCreateWindow('')
        glutSetCursor(GLUT_CURSOR_NONE)
        glutSetKeyRepeat(GLUT_KEY_REPEAT_OFF)
        glutKeyboardFunc(self.key_down)
        glutKeyboardUpFunc(self.key_up)
        glutPassiveMotionFunc(self.mouse_move)
        glutIdleFunc(self.update)
        glutDisplayFunc(self.update)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.fov, float(self.width) / float(self.height),
                       0.1, self.depth)
        glMatrixMode(GL_MODELVIEW)

    def key_down(self, char, x, y):
        self.keypresses[char.decode('utf-8')] = 1

    def key_up(self, char, x, y):
        self.keypresses[char.decode('utf-8')] = 0

    def mouse_move(self, x, y):
        if x == 400 and y == 300:
            pass
        else:
            glutWarpPointer(400, 300)
            self.camera_rot[0] += (x - 400) / 10
            self.camera_rot[1] += (y - 300) / 10
        if self.camera_rot[1] > 45.0:
            self.camera_rot[1] = 45.0
        if self.camera_rot[1] < -45.0:
            self.camera_rot[1] = -45.0

    def camera_move(pos_lambda):
        def camera(*args):
            x, y, z = pos_lambda() * (-1, -1, 1)
            self.camera_pos = vector([x, z, y])
            self.camera_move(func)
            glutTimerFunc(1000 // 60, camera, 0)
        return camera

    @renderer
    def render(self):
        for obj in self.renders:
            if obj is not None:
                obj.draw()
        # self.hud.render()

    def update(self):
        if self.pipe.poll():
            req = self.pipe.recv()
            if req == 'keypresses':
                self.pipe.send(self.keypresses)
            elif req == 'render':
                self.renders, self.state, (x, y, z) = self.pipe.recv()
                self.camera_pos = vector([-x, z, -y])
                if self.state == 'quit':
                    glutLeaveMainLoop()
            elif req == 'textures':
                for i in range(32, 128):
                    self.texture('font/%03d.png' % i)
                self.pipe.send(self.textures)
        self.render()

    @Memoize
    def texture(self, path: str):
        picture = Image.open(path)
        width, height = picture.size
        pBits = picture.tobytes("raw", "RGBX", 0, -1)
        glEnable(GL_TEXTURE_2D)
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, pBits)
        self.textures[path] = texid
        return texid

    def quit(self):
        glutDestroyWindow(glutGetWindow())
        sys.exit()

    @multiprocess
    def loop(self):
        self.gl_init()
        # glutFullScreen()
        glutMainLoop()
        self.quit()
