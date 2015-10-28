# needed if you're running the OS-X system python
try:
    from AppKit import NSApp, NSApplication
except:
    pass

import cyglfw3 as glfw
from OpenGL.GL import *

if not glfw.Init():
  exit()

window = glfw.CreateWindow(640, 480, 'Hello World')
if not window:
  glfw.Terminate()
  exit()

glfw.MakeContextCurrent(window)
while not glfw.WindowShouldClose(window):
  # Render here
  glClearColor(0.0, 1.0, 0.0, 0.0)
  glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

  # Swap front and back buffers
  glfw.SwapBuffers(window)

  # Poll for and process events
  glfw.PollEvents()

glfw.Terminate()
