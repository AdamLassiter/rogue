#! /usr/bin/env python3
from functools import wraps
from multiprocessing import Process
from time import time
from threading import Thread

import OpenGL.GL as GL
import OpenGL.GLU as GLU
import OpenGL.GLUT as GLUT


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
        GLUT.glutSetWindowTitle("FPS: %02d" % (1 / dtime,))
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
        GL.glLoadIdentity()
        GLU.gluLookAt(*self.camera_offset,
                      *(0.0, 0.0, 0.0),
                      *(0.0, 1.0, 0.0))
        GL.glRotatef(self.camera_rot[1], -1.0, 0.0, 0.0)
        GL.glRotatef(self.camera_rot[0], 0.0, 1.0, 0.0)
        GL.glTranslatef(*(self.camera_pos))
        func(self, *args, **kwargs)
        GLUT.glutSwapBuffers()
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
