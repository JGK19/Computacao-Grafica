import pygame
from OpenGL.GL import *
import numpy as np
from VAR import *
from OpenGL.GL.shaders import compileProgram, compileShader



class App:
    def __init__(self):
        # initialize pygame
        pygame.init()
        pygame.display.set_mode(SCREEN_RESOLUTION, pygame.OPENGL|pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

        # initialize opengl
        glClearColor(0.1, 0.2, 0.2, 1)
        self.shader = self.createShader(VERTEX_PATH, FRAGMENT_PATH)
        glUseProgram(self.shader)
        self.triangule = Triangule()
        self.mainLoop()

    def createShader(self, vertexFilepath, fragmentFilepath):

        with open(vertexFilepath, 'r') as f:
            vertex_src = f.readlines()
        
        with open(fragmentFilepath, 'r') as f:
            fragment_src = f.readlines()
        
        shader = compileProgram(
            compileShader(vertex_src, GL_VERTEX_SHADER),
            compileShader(fragment_src, GL_FRAGMENT_SHADER),
        )

        return shader

    def mainLoop(self):

        running = True 
        
        while (running): 
            # handle events
            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    running = False

            # refresh screen
            glClear(GL_COLOR_BUFFER_BIT)

            self.triangule.draw(self.shader)
            pygame.display.flip()

            #timing
            self.clock.tick(60)
        
        self.quit()

    def quit(self):
        self.triangule.destroy()
        glDeleteProgram(self.shader)
        pygame.quit()

class Triangule:

    def __init__(self):

        # tuple of vertices, vertices are not just positions,
        # are all the data we want to store in each point of a primitive, position, color, texture and etc
        # x, y, z r, g, b
        # z = 0 equals flat
        self.vertices = (
            -0.5, -0.5, 0.0, 1.0, 0.0, 0.0,
            0.5, -0.5, 0.0, 0.0, 1.0, 0.0,
            0.0, 0.5, 0.0, 0.0, 0.0, 1.0,
        )

        # graphcs card cant read tuples, but can read arrays, there is no built in data type in python for this, i think
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vertex_count = 3

        # what the numbers in array mean? 
        # search later about lines 60 and 61
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        self.vbo = glGenBuffers(1) #generate one buffer for us, a basic storage container?
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo) # binding the buffer, talking about GL_ARRAY_BUFFER is talking about self.vbo

         # ship our vertices to the graphcs card, (where load, how many bytes, pass data, how we plan use the data)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # enable attribute and then describe how it is laid out in the vbo
        glEnableVertexAttribArray(0) # enable attribute position 
        # what mean (attr, how many points are in each attr, data type, normalize?, howmanybytes to get the next point or color "stride", offset where data begin)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

        # enable attribute color
        glEnableVertexAttribArray(1)
        # what mean (attr, how many points are in each attr, data type, normalize?, howmanybytes to get the next point or color "stride", offset where data begin)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def draw(self, shader):
        glUseProgram(shader)
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))

