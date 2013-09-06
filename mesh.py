import pygame
import math
from OpenGL.GL import *

class ObjMesh(object):
    def __init__(self,filename, scale, offset):
        vertices = []
        faces = []
        norm_normals = []
        for line in file(filename):
            if line[0] == '#':
                continue
            if line.startswith('v '):
                vert = map(float, line.split()[1:4])
                for i in xrange(3):
                    vert[i] = vert[i] * scale[i] + offset[i]
                vertices.append(vert)
                continue
            if line.startswith('vn '):
                vert = map(float, line.split()[1:4])
                norm_normals.append(vert)
            if line.startswith('f '):
                vtps = [tuple(map(int, vtp.split('//'))) for vtp in line.split()[1:4]]
                faces.append(vtps)
                continue

        normals = [[0, 0, 0, 0]] * len(vertices)
        for face in faces:
            v0 = vertices[face[0][0] - 1]
            v1 = vertices[face[1][0] - 1]
            v2 = vertices[face[2][0] - 1]
            dv = [x - y for x, y in zip(v1, v0)]
            dw = [x - y for x, y in zip(v2, v0)]
            n = [dv[1] * dw[2] - dv[2] * dw[1], 
                 dv[2] * dw[0] - dv[0] * dw[2], 
                 dv[0] * dw[1] - dv[1] * dw[0]]
            for i in xrange(3):
                normals[face[i][0] - 1] = [
                    x + y for x, y in zip(normals[face[i][0] - 1], n + [1])]

        test_norm_normals = []
        for n in normals:
            if n[3] != 0:
                n[0] /= n[3]
                n[1] /= n[3]
                n[2] /= n[3]
            d = math.sqrt(n[0]*n[0] + n[1]*n[1] + n[2]*n[2])
            if d != 0:
                n[0] /= d
                n[1] /= d
                n[2] /= d
            test_norm_normals.append(n[:3])

        print len(test_norm_normals)
        print len(vertices)

        vtp_seen = {}
        gl_vertices = []
        gl_indices = []
        num_v = 0
        for face in faces:
            for vtp in face:
                if vtp not in vtp_seen:
                    v = vertices[vtp[0]-1]
                    gl_vertices += v
                    #n = test_norm_normals[vtp[0]-1]
                    #gl_vertices += n
                    vtp_seen[vtp] = num_v
                    num_v += 1
                gl_indices.append(vtp_seen[vtp])

        self.vbo, self.ibo, self.vnbo = glGenBuffers(3)
        vbuf = (ctypes.c_float * (num_v * 3))()
        self.count = 0

        for i, v in enumerate(gl_vertices):
            vbuf[i] = v

        #for i, v in enumerate(gl_vertices):
        #    print v
        #    vbuf[self.count] = v
        #    self.count += 1

        #self.tmp = self.count
        #print len(norm_normals)

        #for v in norm_normals:
        #    for vn in v:
        #        vbuf[self.tmp] = vn
        #        self.tmp += 1

        ibuf = (ctypes.c_uint * len(gl_indices))()
        for i, v in enumerate(gl_indices):
            ibuf[i] = v

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(vbuf), vbuf, GL_STATIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, ctypes.sizeof(ibuf), ibuf, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        self.num_vert = len(gl_indices)
        self.r = 0

    def Render(self, center, scale, forward):
        F = ctypes.sizeof(ctypes.c_float)
        FP = lambda x: ctypes.cast(x * F, ctypes.POINTER(ctypes.c_float))

        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

        glEnableClientState(GL_VERTEX_ARRAY)
        #glEnableClientState(GL_NORMAL_ARRAY)

        glVertexPointer(3, GL_FLOAT, 3 * F, FP(0))
        #glNormalPointer(GL_FLOAT, 6 * F, FP(3))

        #for i in xrange(0, self.count):
        #    glVertexPointer(3, GL_FLOAT, 6 * F, FP(0))
        #for i in xrange(self.count, self.tmp):
        #    glNormalPointer(GL_FLOAT, 6 * F, FP(3))

        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_NORMALIZE)


        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glPushMatrix()
        glTranslate(center[0], center[1], center[2])
        glMultMatrixd([forward[1], -forward[0], 0, 0,
                       -forward[0], -forward[1], 0, 0,
                       0, 0, 1, 0,
                      0, 0, 0, 1])
        glRotate(90, 1, 0, 0)
        glScale(scale[0], scale[1], scale[2])
        glEnable(GL_CULL_FACE)
        glCullFace(GL_FRONT)
        glDepthFunc(GL_LESS)
        glDrawElements(GL_TRIANGLES, self.num_vert, GL_UNSIGNED_INT, None)
        #glDrawLine(GL_LINES, self.num_vert, GL_UNSIGNED_INT, None)
        glPopMatrix()

        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

        glDisable(GL_NORMALIZE)
        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_CULL_FACE)
        glDepthFunc(GL_ALWAYS)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

        glDisableClientState(GL_VERTEX_ARRAY)
        #glDisableClientState(GL_NORMAL_ARRAY)
