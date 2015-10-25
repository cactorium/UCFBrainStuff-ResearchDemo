# needed if you're running the OS-X system python
try:
    from AppKit import NSApp, NSApplication
except:
    pass

import cyglfw3 as glfw
if not glfw.Init():
    exit()

window = glfw.CreateWindow(640, 480, 'Hello World')
if not window:
    glfw.Terminate()
    exit()

glfw.MakeContextCurrent(window)
while not glfw.WindowShouldClose(window):
    # Render here

    # Swap front and back buffers
    glfw.SwapBuffers(window)

    # Poll for and process events
    glfw.PollEvents()

glfw.Terminate()
