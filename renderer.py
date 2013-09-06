import pygame
from OpenGL.GL import *


def CompileShader(src, kind):
  shader = glCreateShader(kind)
  glShaderSource(shader, [src])
  glCompileShader(shader)
  if not glGetShaderiv(shader, GL_COMPILE_STATUS):
    print 'failed to compile shader: %s' % glGetShaderInfoLog(shader)
  return shader


def CompileProgram(vsrc, fsrc):
  program = glCreateProgram()

  if vsrc:
    vshader = CompileShader(vsrc, GL_VERTEX_SHADER)
    glAttachShader(program, vshader)
    glDeleteShader(vshader)
  if fsrc:
    fshader = CompileShader(fsrc, GL_FRAGMENT_SHADER)
    glAttachShader(program, fshader)
    glDeleteShader(fshader)

  glLinkProgram(program)
  glValidateProgram(program)
  return program


moonlight_vshader = """
#version 110

varying vec4 position;
varying vec2 texcoord;

void main() {
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
  position = gl_Vertex;
  texcoord = gl_MultiTexCoord0.st;
}
"""

moonlight_fshader = """
#version 110

varying vec4 position;
varying vec2 texcoord;

uniform sampler2D tex;

uniform vec4 ambient;

uniform float moon1_blend;
uniform vec4 moon1_color;
uniform sampler2D moon1_1, moon1_2;

void main() {
  vec4 color = texture2D(tex, texcoord);
  vec4 light_pos = position / 2048.;

  vec4 light = ambient;

  float light1 = texture2D(moon1_1, light_pos.xy).a;
  light1 = 1. - clamp(light1 * 20., 0., 1.);

  float light2 = texture2D(moon1_2, light_pos.xy).a;
  light2 = 1. - clamp(light2 * 20., 0., 1.);

  light += moon1_color * mix(light1, light2, moon1_blend);

  gl_FragColor = color * light;
}
"""


class Render(object):
  def __init__(self, screen):
    width = screen.get_width()
    height = screen.get_height()
    glViewport(0, 0, width, height)
    glClear(GL_COLOR_BUFFER_BIT)
    pygame.display.flip()
    self.aspect_ratio = width / float(height)

    # We hand out all texture ids here by 'user' and never delete any
    # of them toavoid problems with trying to make sure we don't leak
    # them as objects get created and destroyed.
    self.lightmap_ids = {}

    self.moonlight_program = CompileProgram(
      moonlight_vshader, moonlight_fshader)

  def SetupProjection(self, x, y, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(-self.aspect_ratio, self.aspect_ratio,
               -1, 1,
               1, height + 4)
    glTranslate(-x, -y, -height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

  def LoadTexture(self, path):
    s = pygame.image.load(path)
    id = glGenTextures(1)
    raw = pygame.image.tostring(s, 'RGBA', 1)
    w, h = s.get_width(), s.get_height()
    glBindTexture(GL_TEXTURE_2D, id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                    GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                    GL_LINEAR_MIPMAP_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA,
                 GL_UNSIGNED_BYTE, raw)
    return id

  def LightmapTextureIds(self, index):
    if index not in self.lightmap_ids:
      self.lightmap_ids[index] = glGenTextures(3)
    return self.lightmap_ids[index]

  def SetMoonlightShader(self, ambient, moons):
    prg = self.moonlight_program
    glUseProgram(prg)

    loc = glGetUniformLocation(prg, 'ambient')
    glUniform4f(loc, *ambient)

    m = moons[0]

    loc = glGetUniformLocation(prg, 'moon1_blend')
    glUniform1f(loc, m.blend)

    loc = glGetUniformLocation(prg, 'moon1_color')
    glUniform4f(loc, m.color[0], m.color[1], m.color[2], 1.0)

    loc = glGetUniformLocation(prg, 'moon1_1')
    glUniform1i(loc, 1)
    glActiveTexture(GL_TEXTURE1)
    glBindTexture(GL_TEXTURE_2D,
                  m.lightmaps[m.active_lightmap].id)

    loc = glGetUniformLocation(prg, 'moon1_2')
    glUniform1i(loc, 2)
    glActiveTexture(GL_TEXTURE2)
    glBindTexture(GL_TEXTURE_2D,
                  m.lightmaps[m.next_lightmap].id)

    glActiveTexture(GL_TEXTURE0)
    loc = glGetUniformLocation(prg, 'tex')
    glUniform1i(loc, 0)
