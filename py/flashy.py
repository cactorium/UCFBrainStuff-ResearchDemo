#flashy.py
# needed if you're running the OS-X system python

'''
try:
    from AppKit import NSApp, NSApplication
except:
    pass
'''

# import cyglfw3 as glfw
import glfw
import OpenGL.GL as gl
import numpy as np

import gevent

import braingerZone

FLOAT_SIZE = 4
UINT_SIZE = 4

vertex_code = '''
#version 300 es

layout(location = 0) in vec3 vertexPosition_modelspace;

out vec2 fragCoord;

void main() {
    gl_Position.xyz = vertexPosition_modelspace;
    gl_Position.w = 1.0;

    fragCoord = gl_Position.xy;
}
'''

fragment_code = '''
#version 300 es

uniform uint vals;
uniform uint chosen;

in highp vec2 fragCoord;
out highp vec3 color;

void main(){
    uint mask = 0x00000001u;
    uint val = 0u;
    val = (fragCoord.x < 0.0f) ? val : (val + 1u);
    val = (abs(fragCoord.x) < 0.5f) ? val : (val + 2u);
    val = (fragCoord.y < 0.0f) ? val : (val + 4u);
    val = (abs(fragCoord.y) < 0.5f) ? val : (val + 8u);
    mask = mask << val;

    if ((vals & mask) != 0u) {
        color = vec3(1.0f, 1.0f, 1.0f);
    } else {
        color = vec3(0.0f, 0.0f, 0.0f);
    }
    if (val == chosen) {
        if ((vals & mask) != 0u) {
            color = vec3(1.0f, 1.0f, 0.0f);
        }
    }
}
'''

vertex_data = np.array([
    -1.0, 1.0, 0.0,
    1.0,  1.0, 0.0,
    1.0, -1.0, 0.0,
    -1.0, -1.0, 0.0],
    dtype=np.float32)

index_buffer_data = np.array([
    0, 1, 2,
    2, 3, 0],
    dtype=np.uint32)


def window_size_callback(_, width, height):
  print("resize: {} {}".format(width, height))
  gl.glViewport(0, 0, width, height)


def next_msequence63(i):
    lsb = i & 1
    lsb2 = (i & (1 << 5)) >> 5
    return (i >> 1) | ((lsb ^ lsb2) << 5)


def draw_frame(val, chosen):
  gl.glEnableVertexAttribArray(0)
  gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
  gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 0, None)
  gl.glUseProgram(program)
  gl.glUniform1ui(valsId, val)
  gl.glUniform1ui(chosenId, chosen)

  gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ibo)
  gl.glDrawElements(gl.GL_TRIANGLES, 6, gl.GL_UNSIGNED_INT, None)
  gl.glDisableVertexAttribArray(0)


lights = []
for i in range(0, 16):
  v = 1
  for j in range(0, 4*i):
    v = next_msequence63(v)
  lights.append(v)


def pack_lights(ls):
  val = 0
  for idx, l in enumerate(ls):
    val = val | ((l & 1) << idx)
  return val

if not glfw.init():
  exit()

glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

window = glfw.create_window(640, 480, 'Hello World', None, None)
if not window:
  glfw.terminate()
  exit()

glfw.set_window_size_callback(window, window_size_callback)
glfw.make_context_current(window)

program = gl.glCreateProgram()
vertex = gl.glCreateShader(gl.GL_VERTEX_SHADER)
fragment = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

gl.glShaderSource(vertex, vertex_code)
gl.glShaderSource(fragment, fragment_code)

gl.glCompileShader(vertex)
gl.glCompileShader(fragment)
if gl.glGetShaderiv(vertex, gl.GL_COMPILE_STATUS) != gl.GL_TRUE:
  raise RuntimeError(gl.glGetShaderInfoLog(vertex))
if gl.glGetShaderiv(fragment, gl.GL_COMPILE_STATUS) != gl.GL_TRUE:
  raise RuntimeError(gl.glGetShaderInfoLog(fragment))

gl.glAttachShader(program, vertex)
gl.glAttachShader(program, fragment)

gl.glLinkProgram(program)

gl.glDetachShader(program, vertex)
gl.glDetachShader(program, fragment)

vao = gl.glGenVertexArrays(1)
gl.glBindVertexArray(vao)
print("vertex array object: {}".format(vao))

vbo = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
gl.glBufferData(gl.GL_ARRAY_BUFFER,
                vertex_data.size*FLOAT_SIZE,
                vertex_data,
                gl.GL_STATIC_DRAW)
print("vertex vbo object: {}".format(vbo))

ibo = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ibo)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER,
                index_buffer_data.size*UINT_SIZE,
                index_buffer_data,
                gl.GL_STATIC_DRAW)
print("vertex ibo object: {}".format(ibo))

valsId = gl.glGetUniformLocation(program, "vals")
chosenId = gl.glGetUniformLocation(program, "chosen")

print("vals location is {}".format(valsId))
print("chosen location is {}".format(chosenId))

is_sync_frame = [False]
gevent.spawn(braingerZone.emotiv_loop, is_sync_frame)

while not glfw.window_should_close(window):
  # Render here
  gl.glClearColor(0.0, 1.0, 0.0, 0.0)
  gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

  draw_frame(pack_lights(lights), -1)
  is_sync_frame[0] = (lights[0] == 1)
  lights = list(map(next_msequence63, lights))
  # print(lights)
  # Swap front and back buffers
  glfw.swap_buffers(window)

  # Poll for and process events
  glfw.poll_events()

glfw.terminate()
