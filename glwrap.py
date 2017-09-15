#! /usr/bin/env python3

from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *
from PIL import Image


class Cube:
    vertices = (( 0.5, 0.5,-0.5),
                (-0.5, 0.5,-0.5),
                (-0.5, 0.5, 0.5),
                ( 0.5, 0.5, 0.5),
                ( 0.5,-0.5, 0.5),
                (-0.5,-0.5, 0.5),
                (-0.5,-0.5,-0.5),
                ( 0.5,-0.5,-0.5))
    corners = ((0.0, 0.0),
               (1.0, 0.0),
               (1.0, 1.0),
               (0.0, 1.0))
    surfaces = ((0, 1, 2, 3),
                (4 ,5, 6, 7),
                (2, 3, 4, 5),
                (6, 7, 0, 1),
                (1, 2, 5, 6),
                (0, 3, 4, 7))

    def __init__(self, centre, texname):
        self.position = centre
        self.vertices = tuple(tuple(map(sum, zip(vertex, centre)))
                              for vertex in Cube.vertices)
        self.texture = self.build_texture(texname)

    @staticmethod
    def build_texture(path):
        picture = Image.open(path)
        width, height = picture.size
        pBits = picture.tobytes("raw", "RGBX", 0, -1)
        glEnable(GL_TEXTURE_2D)
        texid = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texid)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, 3, width, height, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, pBits)
        return texid

    def draw(self):
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glBegin(GL_QUADS)
        for vertex_ids in Cube.surfaces:
            for tex_coord, vertex in zip(Cube.corners, vertex_ids):
                glTexCoord2f(*tex_coord)
                glVertex3f(*self.vertices[vertex])
        glEnd()


class GlManager:

    def __init__(self, width, height, title='PyCube', fov=45.0):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(width, height)
        glutInitWindowPosition(200, 200)
        glutCreateWindow(title)
        glutDisplayFunc(self.draw)
        glutIdleFunc(self.draw)
        glutKeyboardFunc(self.keypress)
        glClearColor(0.0, 0.0, 0.0, 0.0)
        glClearDepth(1.0)
        glDepthFunc(GL_LESS)
        glEnable(GL_DEPTH_TEST)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(fov, float(width) / float(height), 0.1, 100.0)
        glMatrixMode(GL_MODELVIEW)
        # Python stuff
        self.camera_pos = [0.0, 0.0, -10.0]
        self.camera_angle = [30.0, 30.0, 30.0]
        self.objects = []

    def draw(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(*self.camera_pos)
        glRotatef(30.0, *self.camera_angle)
        for obj in self.objects:
            obj.draw()
        glutSwapBuffers()

    def keypress(self, *args):
        if args[0] == '\033':
            glutDestroyWindow()
            sys.exit()

    def loop(self):
        # glutFullScreen()
        glutMainLoop()


if __name__ == '__main__':
    mgr = GlManager(1280, 720)
    mgr.objects += [Cube((5.0, 0.0, 0.0), 't1.png'), Cube((-5.0, 0.0, 0.0), 't2.png')]
    mgr.loop()
