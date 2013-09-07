import math
import numpy
import sys


def Slices(delta, size):
  if delta < 0:
    return slice(-delta, size), slice(0, delta)
  else:
    return slice(0, size-delta), slice(delta, size)


def main():
  if len(sys.argv) > 1:
    radius = int(sys.argv)
  else:
    radius = 4

  src = sys.stdin.read()
  dst = sys.stdout

  magic, width, height, maxval, data = src.split(None, 4)
  w, h = int(width), int(height)

  a = numpy.fromstring(data, numpy.uint8)
  a.shape = (h, w)
  a = a > 0

  out = numpy.zeros(a.shape, numpy.bool)

  for dx in xrange(-radius, radius + 1, 1):
    for dy in xrange(-radius, radius + 1, 1):
      if math.hypot(dx, dy) > radius:
        continue
      xslices = Slices(dx, w)
      yslices = Slices(dy, h)
      out[yslices[1], xslices[1]] |= a[yslices[0], xslices[0]]

  out.dtype = numpy.uint8
  out *= 255

  dst.write(magic + ' ' + width + ' ' + height + ' ' + maxval + '\n')
  dst.write(out.tostring())


if __name__ == '__main__':
  main()
