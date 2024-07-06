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

