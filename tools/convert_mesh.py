import math
import sys


def Normalize(v):
  d = math.sqrt(v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
  if d:
    return (v[0] / d, v[1] / d, v[2] / d)
  else:
    return (0, 0, 0)


def LoadMesh(filename, scale, offset, axis_order):
  vertices = []
  faces = []
  normals = []
  tvertices = []

  flip = axis_order in ((0, 2, 1), (1, 0, 2), (2, 1, 0))

  def FixVert(v):
    return [v[axis_order[0]], v[axis_order[1]], v[axis_order[2]]]

  for line in file(filename):
    if line[0] == '#':
      continue
    if line.startswith('v '):
      vert = FixVert(map(float, line.split()[1:4]))
      for i in xrange(3):
        vert[i] = vert[i] * scale[i] + offset[i]
      vertices.append(vert)
      continue
    if line.startswith('vn '):
      vert = FixVert(map(float, line.split()[1:4]))
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

      raw_vtps = map(ParseVert, line.split()[1:])
      for i in xrange(len(raw_vtps) - 2):
        faces.append((raw_vtps[0], raw_vtps[i + 1], raw_vtps[i + 2]))

      #vtps = map(ParseVert, line.split()[1:4])
      #faces.append(vtps)
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
    if flip:
      face = list(reversed(face))
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
  for i, f in enumerate(gl_vertices):
    out.write('%0.5f' % f)
    if (i & 7) == 7:
      out.write('\n')
    else:
      out.write(' ')
  out.close()

  out = file(filename + '.idx', 'w')
  for i, vi in enumerate(gl_indices):
    out.write('%i' % vi)
    if i % 10 == 9:
      out.write('\n')
    else:
      out.write(' ')
  out.write('\n')
  out.close()


def main():
  filename = sys.argv[1]
  if len(sys.argv) > 2:
    scale = tuple(map(float, sys.argv[2].split(',')))
  else:
    scale = (1, 1, 1)
  if len(sys.argv) > 3:
    offset = tuple(map(float, sys.argv[3].split(',')))
  else:
    offset = (0, 0, 0)

  if len(sys.argv) > 4:
    axis_order = tuple(map(int, sys.argv[4].split(',')))
  else:
    axis_order = (0, 1, 2)

  LoadMesh(filename, scale, offset, axis_order)


if __name__ == '__main__':
  main()
