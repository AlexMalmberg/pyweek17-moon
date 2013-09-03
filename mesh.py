import pygame
from OpenGL.GL import *

def loadOBJ(filename):
    vertices = []
    texture_vertices = []
    normals = []
    faces = []
    for line in file(filename):
        vals = line.split()
        if line.startswith('#'): continue
        if line.startswith('v '):
            vert = map(float, vals[1:4])
            vertices.append(vert)
            continue
        if line.startswith('vt '):
            vert = map(float, vals[1:4])
            texture_vertices.append(vert)
            continue
        if line.startswith('vn '):
            vert = map(float, vals[1:4])
            normals.append(vert)
        if line.startswith('f '):
            for f in vals[1:]:
                w = f.split("/")
                vertsOut.append(list(verts[int(w[0])-1]))
                normsOut.append(list(norms[int(w[2])-1]))
        return vertsOut, normsOut

class ObjMesh(object):
    def __init__(self, filename, texture, scale, offset):
        self.vertsOut, self.normsOut = loadOBJ(filename)

    def Render():
        
