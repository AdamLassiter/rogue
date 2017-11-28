#! /usr/bin/env python3

from time import time

import OpenGL.GL as GL
# from OpenGL.arrays import vbo
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT
from PIL import Image

from vector import vector
from wrappers import renderer, Memoize, multiprocess


class GlLight:
    modes = (GL.GL_AMBIENT,
             GL.GL_DIFFUSE,
             GL.GL_SPECULAR)
    lights = (GL.GL_LIGHT0,
              GL.GL_LIGHT1,
              GL.GL_LIGHT2,
              GL.GL_LIGHT3,
              GL.GL_LIGHT4,
              GL.GL_LIGHT5,
              GL.GL_LIGHT6,
              GL.GL_LIGHT7)

    def __init__(self, centre: vector, colors: tuple, lightid: int) -> None:
        self.position = centre
        self.colors = colors
        self.light = lightid

    def draw(self):
        GL.glEnable(self.light)
        for mode, color in zip(GlLight.modes, self.colors):
            GL.glLightfv(self.light, mode, color)
        GL.glLightfv(self.light, GL.GL_POSITION, self.position)

    @property
    def position(self):
        x, y, z = self.pos
        return vector([x, z, y])

    @position.setter
    def position(self, v: vector):
        x, y, z = v
        # self.pos = vector([x, z, y])
        self.pos = vector([0, 0, 3])


class GlObject:
    modes = (GL.GL_AMBIENT,
             GL.GL_DIFFUSE,
             GL.GL_SPECULAR,
             GL.GL_SHININESS,
             GL.GL_EMISSION)
    vertices = [[0.5, 0.5, -0.5],
                [-0.5, 0.5, -0.5],
                [-0.5, 0.5, 0.5],
                [0.5, 0.5, 0.5],
                [0.5, -0.5, 0.5],
                [-0.5, -0.5, 0.5],
                [-0.5, -0.5, -0.5],
                [0.5, -0.5, -0.5]]
    corners = ((1.0, 1.0),
               (0.0, 1.0),
               (0.0, 0.0),
               (1.0, 0.0))
    surfaces = ((0, 1, 2, 3),
                (7, 6, 5, 4),
                (3, 2, 5, 4),
                (1, 0, 7, 6),
                (2, 1, 6, 5),
                (0, 3, 4, 7))

    def __init__(self, centre: vector, colors: tuple, texid: int) -> None:
        self.colors = colors
        self.position = vector(centre)
        self.texture = texid

    def draw(self):
        for mode, color in zip(GlObject.modes, self.colors):
            GL.glMaterialfv(GL.GL_FRONT, mode, color)
        GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
        GL.glBegin(GL.GL_QUADS)
        for vertex_ids in GlObject.surfaces:
            for tex_coord, vertex in zip(GlObject.corners, vertex_ids):
                GL.glTexCoord2f(*tex_coord)
                # GL.glColor4f(1, 1, 1, 0)
                GL.glVertex3f(*self.vertices[vertex])
        GL.glEnd()

    @property
    def position(self):
        x, y, z = self.pos
        return vector([x, z, y])

    @position.setter
    def position(self, v: vector):
        x, y, z = v
        self.pos = vector([x, z, y])
        self.vertices = [list(map(sum, zip(vertex, self.pos)))
                         for vertex in GlObject.vertices]


class GlManager:

    def __init__(self, pipe, width: int, height: int, fov=45.0, depth=20.0) -> None:
        self.pipe = pipe
        self.fps = time()
        self.camera_pos = vector([0.0, 0.0, 0.0])
        self.camera_offset = vector([0, 10.0, -10.0])
        self.camera_rot = [180.0, 0.0]
        self.textures: dict = {}
        self.keypresses: dict = {}
        self.lights: list = []
        self.renders: list = []
        # OpenGL stuff
        self.width, self.height = width, height
        self.fov, self.depth = fov, depth

    def gl_init(self):
        GLUT.glutInit()
        GLUT.glutInitDisplayMode(GLUT.GLUT_RGBA | GLUT.GLUT_DOUBLE | GLUT.GLUT_DEPTH)
        GLUT.glutInitWindowSize(self.width, self.height)
        GLUT.glutInitWindowPosition(200, 200)
        GLUT.glutCreateWindow('')
        GLUT.glutSetCursor(GLUT.GLUT_CURSOR_NONE)
        GLUT.glutSetKeyRepeat(GLUT.GLUT_KEY_REPEAT_OFF)
        GLUT.glutKeyboardFunc(self.key_down)
        GLUT.glutKeyboardUpFunc(self.key_up)
        GLUT.glutPassiveMotionFunc(self.mouse_move)
        GLUT.glutIdleFunc(self.update)
        GLUT.glutDisplayFunc(self.update)
        GL.glEnable(GL.GL_LIGHTING)
        GL.glShadeModel(GL.GL_SMOOTH)
        GL.glClearColor(0.0, 0.0, 0.0, 0.0)
        GL.glClearDepth(1.0)
        GL.glDepthFunc(GL.GL_LESS)
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glEnable(GL.GL_CULL_FACE)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GLU.gluPerspective(self.fov, float(self.width) / float(self.height),
                           0.1, self.depth)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def key_down(self, char, x, y):
        self.keypresses[char.decode('utf-8')] = 1

    def key_up(self, char, x, y):
        self.keypresses[char.decode('utf-8')] = 0

    def mouse_move(self, x, y):
        if x == 400 and y == 300:
            pass
        else:
            GLUT.glutWarpPointer(400, 300)
            self.camera_rot[0] += (x - 400) / 10
            self.camera_rot[1] += (y - 300) / 10
        if self.camera_rot[1] > 35.0:
            self.camera_rot[1] = 35.0
        if self.camera_rot[1] < -35.0:
            self.camera_rot[1] = -35.0

    def camera_move(self, pos_lambda):
        def camera(*args):
            x, y, z = pos_lambda() * (-1, -1, 1)
            self.camera_pos = vector([x, z, y])
            self.camera_move(pos_lambda)
            GLUT.glutTimerFunc(1000 // 60, camera, 0)
        return camera

    @renderer
    def render(self):
        for light in self.lights:
            light.draw()
        for obj in self.renders:
            if obj is not None:
                obj.draw()

    def update(self):
        if self.pipe.poll():
            req = self.pipe.recv()
            if req == 'keypresses':
                self.pipe.send(self.keypresses)
            elif req == 'render':
                self.lights, self.renders, self.state, (x, y, z) = self.pipe.recv()
                self.camera_pos = vector([-x, -z, -y])
                if self.state == 'quit':
                    GLUT.glutLeaveMainLoop()
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
        GL.glEnable(GL.GL_TEXTURE_2D)
        texid = GL.glGenTextures(1)
        GL.glBindTexture(GL.GL_TEXTURE_2D, texid)
        GL.glTexParameteri(GL.GL_TEXTURE_2D, GL.GL_TEXTURE_MIN_FILTER, GL.GL_LINEAR)
        GL.glTexImage2D(GL.GL_TEXTURE_2D, 0, 3, width, height, 0, GL.GL_RGBA,
                        GL.GL_UNSIGNED_BYTE, pBits)
        self.textures[path] = texid
        return texid

    def quit(self):
        GLUT.glutDestroyWindow(GLUT.glutGetWindow())
        GL.sys.exit()

    @multiprocess
    def loop(self):
        self.gl_init()
        # glutFullScreen()
        GLUT.glutMainLoop()
        self.quit()
