#! /usr/bin/env python3

from functools import wraps
from time import time

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image

from vector import vector


class Cube:
    vertices = ((0.5, 0.5, -0.5),
                (-0.5, 0.5, -0.5),
                (-0.5, 0.5, 0.5),
                (0.5, 0.5, 0.5),
                (0.5, -0.5, 0.5),
                (-0.5, -0.5, 0.5),
                (-0.5, -0.5, -0.5),
                (0.5, -0.5, -0.5))
    corners = ((0.0, 0.0),
               (1.0, 0.0),
               (1.0, 1.0),
               (0.0, 1.0))
    surfaces = ((0, 1, 2, 3),
                (4, 5, 6, 7),
                (2, 3, 4, 5),
                (6, 7, 0, 1),
                (1, 2, 5, 6),
                (0, 3, 4, 7))

    def __init__(self, centre: vector, texid: int):
        self.position = vector([0, 0, 0])
        self.vertices = Cube.vertices
        self.translate(centre)
        self.texture = texid

    def draw(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        for vertex_ids in Cube.surfaces:
            for tex_coord, vertex in zip(Cube.corners, vertex_ids):
                glTexCoord2f(*tex_coord)
                glVertex3f(*self.vertices[vertex])
        glEnd()

    def translate(self, v: vector):
        self.position += v
        self.vertices = tuple(tuple(map(sum, zip(vertex, v)))
                              for vertex in self.vertices)


class GlManager:

    @wraps
    class Memoize:
        def __init__(self, f):
            self.f = f
            self.memo = {}

        def __call__(self, *args, **kwargs):
            if args not in self.memo:
                print(args)
                self.memo[args] = self.f(*args, **kwargs)
            return self.memo[args]

    def __init__(self, width: int, height: int, fov=45.0, depth=100.0):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(width, height)
        glutInitWindowPosition(200, 200)
        glutCreateWindow('')
        glutSetCursor(GLUT_CURSOR_NONE)
        glutDisplayFunc(self.draw)
        glutIdleFunc(self.draw)
        glutPassiveMotionFunc(self.mouse_move)
        glutKeyboardFunc(self.keypress)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(fov, float(width) / float(height), 0.1, depth)
        glMatrixMode(GL_MODELVIEW)
        # Python stuff
        self.fps = time()
        self.camera_pos = [0.0, 15.0, -15.0]
        self.camera_rot = [0.0, 0.0]
        self.objects = []
        self.textures = {}

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

    def draw(self):
        self.fps, dtime = time(), time() - self.fps
        glutSetWindowTitle("FPS: %02d" % (1 / dtime,))
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        gluLookAt(*self.camera_pos, *(0, 0, 0), *(0, 1, 0))
        glRotatef(self.camera_rot[1], -1.0, 0.0, 0.0)
        glRotatef(self.camera_rot[0], 0.0, 1.0, 0.0)
        for obj in self.objects:
            obj.draw()
        glutSwapBuffers()

    def keypress(self, *args):
        if args[0] == '\033':
            glutDestroyWindow()
            sys.exit()

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

    def loop(self):
        glutFullScreen()
        glutMainLoop()

    def add(self, obj):
        self.objects.append(obj)


if __name__ == '__main__':
    mgr = GlManager(1280, 720, depth=100)
    for x in range(-10, 11):
        for z in range(-10, 11):
            mgr.add(Cube((x, 0.0, z),
                         mgr.texture('t1.png' if (x + z) % 2 else 't2.png')))
    mgr.loop()
