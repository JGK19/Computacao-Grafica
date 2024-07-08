class Line:
    def __init__(self):
        pass
    def draw():
        glColor3f(0.0, 0.0, 0.0)
        glBegin(GL_LINES)
        glVertex2i(0, 0)
        glVertex2i(100, 20)
        glEnd()
        glFlush()