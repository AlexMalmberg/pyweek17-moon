import math
import sys


def Normalize(v):
  d = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
  return (v[0] / d, v[1] / d, v[2] / d)


def LoadMesh(filename, scale, offset):
  vertices = []
  faces = []
  normals = []
  tvertices = []

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
      for i in xrange(3):
        vert[i] = vert[i] * scale[i]
      vert = Normalize(vert)
      normals.append(vert)
    if line.startswith('vt '):
      vert = map(float, line.split()[1:3])
      tvertices.append(vert)
    if line.startswith('f '):
      def ParseVert(s):
        temp = s.split('/')
        while len(temp) < 3:
          temp.append('')
        for i in xrange(3):
          try:
            temp[i] = int(temp[i])
          except ValueError:
            temp[i] = 1
        return tuple(temp)
      vtps = map(ParseVert, line.split()[1:4])
      faces.append(vtps)
      continue

  print ('%i vertices, %i normals, %i tvertices, %i faces'
         % (len(vertices), len(normals), len(tvertices), len(faces)))

  bounds_min = vertices[0][:]
  bounds_max = vertices[0][:]
  for v in vertices:
    for i in xrange(3):
      bounds_min[i] = min(bounds_min[i], v[i])
      bounds_max[i] = max(bounds_max[i], v[i])

  print ('bounds: %0.2f, %0.2f, %0.2f -- %0.2f, %0.2f, %0.2f'
         % (bounds_min[0], bounds_min[1], bounds_min[2],
            bounds_max[0], bounds_max[1], bounds_max[2]))

  if not normals:
    print 'using dummy normals'
    normals.append((1, 0, 0))
  if not tvertices:
    print 'using dummy texture coords'
    tvertices.append((0, 0))

  vtp_seen = {}
  # 3 x position, 3 x normal, 2 x tvertex for each vertex.
  gl_vertices = []
  gl_indices = []
  num_v = 0
  for face in faces:
    for vtp in face:
      if vtp not in vtp_seen:
        v = vertices[vtp[0] - 1]
        gl_vertices += v
        gl_vertices += normals[vtp[2] - 1]
        gl_vertices += tvertices[vtp[1] - 1]
        vtp_seen[vtp] = num_v
        num_v += 1
      gl_indices.append(vtp_seen[vtp])

  print ('%i gl vertices (%i floats), %i indices'
         % (num_v, len(gl_vertices), len(gl_indices)))

  out = file(filename + '.vert', 'w')
  for f in gl_vertices:
    out.write(' %0.5f' % f)
  out.write('\n')
  out.close()

  out = file(filename + '.idx', 'w')
  for i in gl_indices:
    out.write(' %i' % i)
  out.write('\n')
  out.close()


def main():
  filename = sys.argv[1]
  if len(sys.argv) > 2:
    scale = tuple(map(float, sys.argv[2].split(',')))
  else:
    scale = (1, 1, 1)
  if len(sys.argv) > 3:
    offset = tuple(map(float, sys.argv[2].split(',')))
  else:
    offset = (0, 0, 0)

  LoadMesh(filename, scale, offset)


if __name__ == '__main__':
  main()
