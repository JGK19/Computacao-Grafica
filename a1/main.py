import pygame
from OpenGL.GL import *
import numpy as np
from VAR import *
from OpenGL.GL.shaders import compileProgram, compileShader

import pyrr

class Cube:

    def __init__(self, position, eulers):
        self.position = np.array(position, dtype=np.float32)
        self.eulers = np.array(eulers, dtype=np.float32)

class App:

    def __init__(self):
        # initialize pygame
        pygame.init()
        pygame.display.set_mode(SCREEN_RESOLUTION, pygame.OPENGL|pygame.DOUBLEBUF)
        self.clock = pygame.time.Clock()

        # initialize opengl
        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_BLEND) #thats to enable png things
        glEnable(GL_DEPTH_TEST) #drawing things in front of eachother propeçy
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA) #thats to enable png things # standart functions to alpha blending
        self.shader = self.createShader(VERTEX_PATH, FRAGMENT_PATH)
        glUseProgram(self.shader)
        glUniform1i(glGetUniformLocation(self.shader, "imageTexture"), 0)

        self.cube = Cube(
            position=[0,0,-4],
            eulers=[0,0,0],
        )

        self.cube_mesh = Mesh("models/testcube.obj")

        self.duck_texture = Material("gfx/patoteste1.png")
        #self.duckpng_texture = Material("gfx/patoteste.png")

        projection_transform = pyrr.matrix44.create_perspective_projection( # magical matrix i could have done this myself somehow
            fovy = 45, aspect = SCREEN_RESOLUTION[0]/SCREEN_RESOLUTION[1], 
            near = 0.1, far = 10, dtype = np.float32,
        )

        glUniformMatrix4fv( # passing to the shaders scripts i think (that thing, qtd matrix, GL_FALSE, actually the matrix)
            glGetUniformLocation(self.shader, "projection"),
            1, GL_FALSE, projection_transform
        )

        self.modelMatrixLocation = glGetUniformLocation(self.shader, "model")



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
                

            # update cube
            self.cube.eulers[2] += 0.2
            if (self.cube.eulers[2] > 360):
                self.cube.eulers[2] -= 360

            # refresh screen
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)



            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(self.cube.eulers),
                    dtype=np.float32,
                )
            )

            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_translation(
                    vec=self.cube.position,
                    dtype=np.float32,
                )
            )

            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transform)
            glBindVertexArray(self.cube_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)
            
            model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_eulers(
                    eulers=np.radians(self.cube.eulers),
                    dtype=np.float32,
                )
            )

            model_transform = pyrr.matrix44.multiply(
                m1=model_transform,
                m2=pyrr.matrix44.create_from_translation(
                    vec=self.cube.position,
                    dtype=np.float32,
                )
            )

            glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, model_transform)
            glBindVertexArray(self.cube_mesh.vao)
            glDrawArrays(GL_TRIANGLES, 0, self.cube_mesh.vertex_count)

            pygame.display.flip()

            #timing
            self.clock.tick(60)
        
        self.quit()

    def quit(self):
        self.cube_mesh.destroy()
        self.duck_texture.destroy()
        glDeleteProgram(self.shader)
        pygame.quit()

class Mesh:

    def __init__(self, filename):
        # x, y, z, s, t, nx, ny, nz
        self.vertices = self.loadMesh(filename)
        self.vertex_count = len(self.vertices) // 8
        self.vertices = np.array(self.vertices, dtype=np.float32)

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # vertices
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        # position
        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        
        #texture
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
    
    def loadMesh(self, filename: str) -> list[float]:

        vertices = []

        v = []
        vt = []
        vn = []

        with open(filename, "r") as file:
            line = file.readline()

            while line:
                words = line.split(" ")
                if words[0] == "v":
                    v.append(self.read_vertex_data(words))
                elif words[0] == "vt":
                    vt.append(self.read_textcoord_data(words))
                elif words[0] == "vn":
                    vn.append(self.read_normal_data(words))
                elif words[0] == "f":
                    self.read_face_data(words, v, vt, vn, vertices)
                line = file.readline()

        return vertices

    def read_face_data(
        self, words: list[str], 
        v: list[list[float]], vt: list[list[float]], 
        vn: list[list[float]], vertices: list[float]) -> None:
        
        triangleCount = len(words) - 3

        for i in range(triangleCount):

            self.make_corner(words[1], v, vt, vn, vertices)
            self.make_corner(words[2 + i], v, vt, vn, vertices)
            self.make_corner(words[3 + i], v, vt, vn, vertices)
        
    def make_corner(
        self, corner_description: str, 
        v: list[list[float]], vt: list[list[float]], 
        vn: list[list[float]], vertices: list[float]) -> None:

        v_vt_vn = corner_description.split("/")
        for element in v[int(v_vt_vn[0]) - 1]:
            vertices.append(element)
        for element in vt[int(v_vt_vn[1]) - 1]:
            vertices.append(element)
        for element in vn[int(v_vt_vn[2]) - 1]:
            vertices.append(element)
    
    def read_vertex_data(self, words: list[str]) -> list[float]:

        return [
            float(words[1]),
            float(words[2]),
            float(words[3]),
        ]
    
    def read_textcoord_data(self, words: list[str]) -> list[float]:

        return [
            float(words[1]),
            float(words[2]),
        ]
    
    def read_normal_data(self, words: list[str]) -> list[float]:

        return [
            float(words[1]),
            float(words[2]),
            float(words[3]),
        ]
    


    def draw(self, shader, texture):
        glUseProgram(shader)
        if texture != None:
            texture.use()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)
     
    def draw(self, shader, texture):
        glUseProgram(shader)
        if texture != None:
            texture.use()
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, self.vertex_count)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))


class Material:

    def __init__(self, filepath):
        self.texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

        image = pygame.image.load(filepath).convert_alpha() #only .convert() does not handle transparency, so using convert_alpha()
        image_width, image_height = image.get_rect().size
        image_data = pygame.image.tostring(image, "RGBA")
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image_width, image_height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)
    
    def use(self):
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, self.texture)
    
    def destroy(self):
        glDeleteTextures(1, (self.texture,))

if __name__ == '__main__':
    app = App()
