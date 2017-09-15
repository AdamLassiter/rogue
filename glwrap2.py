from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
 
ESCAPE = '\033'
 
window = 0
 
#rotation
X_AXIS = 0.0
Y_AXIS = 0.0
Z_AXIS = 0.0
 
DIRECTION = 1


def buildTexture(path):
    from PIL import Image

    try:
        Picture = Image.open(path)
    except:
        print("Unable to open image file '%s'." % path)
        return False, 0
    glMaxTexDim = glGetIntegerv(GL_MAX_TEXTURE_SIZE)
    WidthPixels = Picture.size[0]
    HeightPixels = Picture.size[1]
    if WidthPixels > HeightPixels:
        resizeWidthPixels = next_p2(WidthPixels)
        squash = float(resizeWidthPixels) / float(WidthPixels)
        resizeHeightPixels = int(HeighPixels * squash)
    else:
        resizeHeightPixels = next_p2(HeightPixels)
        squash = float(resizeHeightPixels) / float(HeightPixels)
        resizeWidthPixels = int(WidthPixels * squash)
    Picture = Picture.resize((resizeWidthPixels, resizeHeightPixels), Image.BICUBIC)
    lWidthPixels = next_p2(resizeWidthPixels)
    lHeightPixels = next_p2(resizeWidthPixels)
    newpicture = Image.new("RGB", (lWidthPixels, lHeightPixels), (0, 0, 0))
    newpicture.paste(Picture)
    pBits = newpicture.tobytes("raw", "RGBX", 0, -1)
    texid = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, texid)
    glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, lWidthPixels, lHeightPixels, 0, GL_RGBA, GL_UNSIGNED_BYTE, pBits)
    return True, texid
 
 
def initGL(width, height):
    buildTexture('texture.png')
    glEnable(GL_TEXTURE_2D)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glShadeModel(GL_SMOOTH)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45.0, float(width)/float(height), 0.1, 1000.0)
    glMatrixMode(GL_MODELVIEW)


def next_p2 (num):
    """ If num isn't a power of 2, will return the next higher power of two """
    rval = 1
    while (rval<num):
        rval <<= 1
    return rval


def drawGLScene():
    global X_AXIS, Y_AXIS, Z_AXIS
    global DIRECTION, CUBE
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0.0,0.0,-20.0)
    glRotatef(X_AXIS,1.0, 0.0, 0.0)
    glRotatef(Y_AXIS,0.0, 1.0, 0.0)
    glRotatef(Z_AXIS,0.0, 0.0, 1.0)
    for cube in CUBES:
        cube.draw()
    X_AXIS -= 0.30
    Z_AXIS -= 0.30
    glutSwapBuffers()


def keyPressed(*args):
    if args[0] == ESCAPE:
        sys.exit()


class Cube:
    vertices = (( 0.5, 0.5,-0.5),
                (-0.5, 0.5,-0.5),
                (-0.5, 0.5, 0.5),
                ( 0.5, 0.5, 0.5),
                ( 0.5,-0.5, 0.5),
                (-0.5,-0.5, 0.5),
                (-0.5,-0.5,-0.5),
                ( 0.5,-0.5,-0.5))

    tex_coords = ((0.0, 0.0),
                  (1.0, 0.0),
                  (1.0, 1.0),
                  (0.0, 1.0))

    surfaces = ((0, 1, 2, 3),
                (4 ,5, 6, 7),
                (2, 3, 4, 5),
                (6, 7, 0, 1),
                (1, 2, 5, 6),
                (0, 3, 4, 7))

    def __init__(self, centre):
        self.position = centre
        self.vertices = tuple(tuple(map(sum, zip(vertex, centre)))
                              for vertex in Cube.vertices)

    def draw(self):
        glBegin(GL_QUADS)
        for vertex_ids in Cube.surfaces:
            for tex_coord, vertex in zip(Cube.tex_coords, vertex_ids):
                glTexCoord2f(*tex_coord)
                glVertex3f(*self.vertices[vertex])
        glEnd()


CUBES = tuple(Cube((0.0, 0.0, -z)) for z in range(100))


def main():
    global window
 
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
    glutInitWindowSize(1280, 720)
    window = glutCreateWindow('OpenGL Python Cube')
    glutDisplayFunc(drawGLScene)
    glutIdleFunc(drawGLScene)
    glutKeyboardFunc(keyPressed)
    initGL(1280, 720)
    glutFullScreen()
    glutMainLoop()


if __name__ == "__main__":
    main()
