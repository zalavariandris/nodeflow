import sys
import numpy as np

# Opengl
from OpenGL.GL import *
import glm
import ctypes

# PySide
from PySide2.QtWidgets import QOpenGLWidget, QApplication
from PySide2.QtGui import QMouseEvent,QWheelEvent
from PySide2.QtCore import Qt

from glhelpers import make_texture

# Helpers
def ray_plane_intersection(p0:glm.vec3, p1:glm.vec3, p_co:glm.vec3, p_no:glm.vec3, epsilon:float = 1e-6)->glm.vec3:
    """
    p0, p1 : Define the line.
    p_co, p_no : define the plane :
    p_co Is a point on the plane(plane coordinate).
    p_no Is a normal vector defining the plane direction;
    (does not need to be normalized).
    Return a Vector or None(when the intersection can't be found).
    """
    u:glm.vec3 = p1 - p0
    dot = glm.dot(p_no, u)

    if abs(dot) > epsilon:
        """
        The factor of the point between p0->p1(0 - 1)
        if 'fac' is between (0 - 1) the point intersects with the segment.
        Otherwise:
            < 0.0: behind p0.
            > 1.0: infront of p1.
        """
        w = p0 - p_co
        fac = -glm.dot(p_no, w) / dot
        u = u * fac
        return p0 + u

    else:
        """The segment is parallel to plane."""
        return glm.vec3(0, 0, 0)


class Camera:
    def __init__(self,):
        self.eye = glm.vec3(0, 0, -5)
        self.target = glm.vec3(0, 0, 0)
        self.up = glm.vec3(0, 1, 0)
        self.fovy = 1.57 / 2
        self.tiltshift = glm.vec2(0.0, 0.0)
        self.aspect = 1.0
        self.near_plane = 0.1
        self.far_plane = 10000
        self.ortho = False

    @property
    def fovx(self):
        return 2 * glm.atan(glm.tan(self.fovy / 2) * self.aspect)

    def get_projection(self):
        if self.ortho:
            target_distance = glm.distance(self.eye, self.target)
            t = glm.tan(self.fovy / 2) * target_distance
            return glm.ortho(
                -1.0 * self.aspect * t,
                +1.0 * self.aspect * t,
                -1.0 * t,
                +1.0 * t,
			self.near_plane, self.far_plane)
        else:
            tilt = self.tiltshift * self.near_plane
            t = glm.tan(self.fovy / 2)
            return glm.frustum(
                -1.0 * self.aspect * t * self.near_plane,
                +1.0 * self.aspect * t * self.near_plane,
                -1.0 * t * self.near_plane,
                +1.0 * t * self.near_plane,
                self.near_plane, self.far_plane); # left right, bottom, top, near, far

    def get_view(self):
        return glm.lookAt(self.eye, self.target, self.up)

    def forward(self)->glm.vec3:
        view = self.get_view()
        return glm.normalize(glm.vec3(view[0][2], view[1][2], view[2][2]))

    def get_target_distance(self):
        return glm.distance(self.eye, self.target)

    def orbit(self, yaw, pitch):
        forward = glm.normalize(self.target - self.eye)
        right = glm.cross(forward, self.up)
        #up = glm::cross(forward, right)

        pivot = self.target
        m = glm.mat4(1)
        m = glm.translate(m, pivot)

        m = glm.rotate(m, yaw, self.up)
        m = glm.rotate(m, pitch, right)

        m = glm.translate(m, -pivot)

        self.eye = glm.vec3(m * glm.vec4(self.eye, 1.0))

    def pan(self, horizontal, vertical):
        view = self.get_view()

        right = glm.vec3(view[0][0], view[1][0], view[2][0])
        up = glm.vec3(view[0][1], view[1][1], view[2][1])
        forward = glm.vec3(view[0][2], view[1][2], view[2][2])

        target_distance = glm.distance(self.eye, self.target)
        offset = right * horizontal*self.aspect - up * vertical
        offset *= glm.tan(self.fovy / 2) * 2
        offset *= target_distance
        self.target += offset
        self.eye += offset

    def screen_to_planeXY(self, mouseX, mouseY, viewport=glm.vec4(-1, -1, 2, 2))->glm.vec3:
        """
        unproject to XY plane to viewport coordinates
        """
        proj:glm.mat4 = self.get_projection()
        view:glm.mat4 = self.get_view()

        near_point:glm.vec3 = glm.unProject(glm.vec3(mouseX, mouseY, 0.0), view, proj, viewport)
        far_point:glm.vec3 = glm.unProject(glm.vec3(mouseX, mouseY, 1.0), view, proj, viewport)

        return ray_plane_intersection(near_point, far_point, { 0,0,0 }, { 0,0,1 })

    def dolly(self, offset:float):
        self.eye = self.eye + self.forward() * offset

    def dolly_to_mouse(self, offset:float, mouseX:float, mouseY:float, viewport:glm.vec4):
        proj = self.get_projection()
        view = self.get_view()

        forw = self.forward()
        near_point = glm.unProject(glm.vec3(mouseX, mouseY, 0.0), view, proj, viewport)
        far_point = glm.unProject(glm.vec3(mouseX, mouseY, 1.0), view, proj, viewport)
        dir = glm.normalize(near_point - far_point)
        self.eye += dir * offset

        self.target = ray_plane_intersection(self.eye, self.eye+forw, glm.vec3(0,0,0), glm.vec3(0,0,1))
        #self.target += dir * (float)offset;

    def to_program(self, program:int, projection_name="projection", view_name="view"):
        projectionLocation = glGetUniformLocation(program, "projection");
        glUniformMatrix4fv(projectionLocation, 1, GL_FALSE, glm.value_ptr(self.get_projection()))
        viewLocation = glGetUniformLocation(program, "view")
        glUniformMatrix4fv(viewLocation, 1, GL_FALSE, glm.value_ptr(self.get_view()))

    def fit(self, width, height):
        camDistance = glm.max(width / 2 / glm.tan(self.fovx / 2), height / 2 / glm.tan(self.fovy / 2))
        self.eye = glm.vec3(width / 2.0, height / 2.0, camDistance)
        self.target = glm.vec3(width / 2.0, height / 2.0, 0.0)


class ImGeo:
    def __init__(self, mode, positions, indices, uvs, normals):
        self.mode = mode
        self.positions = positions
        self.indices = indices
        self.uvs = uvs
        self.normals = normals

    @staticmethod
    def quad():
        positions = np.array([
            (-1,-1, 0), 
            ( 1,-1, 0), 
            ( 1, 1, 0), 
            (-1, 1, 0)
        ], dtype=np.float32)

        uvs = np.array([
            (1,1), (0,1), (0, 0), (1, 0)
        ], dtype=np.float32)

        normals = np.array([
            (0,0,-1), (0,0,-1), (0,0,-1), (0,0,-1)
        ], dtype=np.float32)

        indices = np.array([
            0,1,2, 0,2,3
        ], dtype=np.uint)

        return ImGeo(GL_TRIANGLES, positions, indices, uvs, normals)


class GLViewer(QOpenGLWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GLViewer")
        self.setMouseTracking(True)
        

        self.resize(400, 400)
        self.camera = Camera()
        self.camera.eye=glm.vec3(0, 1, -5)
        self.camera.target=glm.vec3(0,0,0)
        self.camera.ortho=False
        self.model = glm.mat4(1.0)
        self.mouse_pressed = False

        self.mouse_buffer = None
        self.tex = None

    def initializeGL(self):
        gl_version = glGetString(GL_VERSION).decode()
        shading_language_version = glGetString(GL_SHADING_LANGUAGE_VERSION).decode()
        print(f"Initalize OpenGL: {gl_version}, {shading_language_version}")
        
        glClearColor(0.2, 0.2, 0.2, 1.0)
        vertex_code = """
            #version 330 core
            in vec3 aPos;
            in vec2 aUV;
            uniform mat4 MVP;

            out vec2 vUV;

            void main()
            {
                vUV = aUV;
                gl_Position = MVP * vec4(aPos, 1.0);
            }
        """
        fragment_code = """
            #version 330 core
            in vec2 vUV;
            uniform sampler2D textureMap;
            out vec4 fragColor;
            void main()
            {
                vec4 tex = texture(textureMap, vUV);
                fragColor = vec4(tex.rgb,1.0);
            }
        """
        self.program = glCreateProgram()
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(vertex_shader, vertex_code)
        glShaderSource(fragment_shader, fragment_code)

        # Compile shaders
        glCompileShader(vertex_shader)
        if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(vertex_shader).decode()
            print(error)
            raise RuntimeError("Shader compilation error")
                        
        glCompileShader(fragment_shader)
        if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(fragment_shader).decode()
            print(error)
            raise RuntimeError("Shader compilation error") 

        # attachs shaders
        glAttachShader(self.program, vertex_shader)
        glAttachShader(self.program, fragment_shader)

        # link program
        glLinkProgram(self.program)
        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            print("LINKING ERROR:", glGetProgramInfoLog(self.program))
            raise RuntimeError('Linking error')

        # detach shaders
        glDetachShader(self.program, vertex_shader)
        glDetachShader(self.program, fragment_shader)

        # VBO
        geo = ImGeo.quad()
        self.geo = geo

        pos_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, pos_vbo)
        glBufferData(GL_ARRAY_BUFFER, geo.positions.nbytes, geo.positions, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        uv_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, uv_vbo)
        glBufferData(GL_ARRAY_BUFFER, geo.uvs.nbytes, geo.uvs, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # EBO
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, geo.indices.nbytes, geo.indices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        self.ebo = ebo

        #VAO
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        loc = glGetAttribLocation(self.program, "aPos")
        if loc >=0:
            glEnableVertexAttribArray(loc)
            glBindBuffer(GL_ARRAY_BUFFER, pos_vbo)
            glVertexAttribPointer(loc, 3, GL_FLOAT, False, geo.positions.strides[0], ctypes.c_void_p(0))
        else:
             print("aPos attribute is not used")

        loc = glGetAttribLocation(self.program, "aUV")
        if loc >=0:
            glEnableVertexAttribArray(loc)
            glBindBuffer(GL_ARRAY_BUFFER, uv_vbo)
            glVertexAttribPointer(loc, 2, GL_FLOAT, False, geo.uvs.strides[0], ctypes.c_void_p(0))
        else:
             print("aUV attribute is not used")
        self.vao = vao

        # set uniforms
        
        glUseProgram(self.program)
        loc = glGetUniformLocation(self.program, "MVP")
        MVP = self.camera.get_projection() * self.camera.get_view()
        glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(MVP))

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT)
        
        glUseProgram(self.program)
        
        MVP = self.camera.get_projection() * self.camera.get_view() * self.model
        loc = glGetUniformLocation(self.program, "MVP")
        glUniformMatrix4fv(loc, 1, GL_FALSE, glm.value_ptr(MVP))

        # draw geometry
        if self.tex is not None: glBindTexture(GL_TEXTURE_2D, self.tex)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glDrawElements(self.geo.mode, self.geo.indices.size, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)

    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)
        self.camera.aspect = w / h

    def mousePressEvent(self, event:QMouseEvent):
        self.mouse_buffer = event.pos()

    def mouseMoveEvent(self, event:QMouseEvent):
        screen_width, screen_height = self.size().width(), self.size().height()
        if self.mouse_buffer == None:
            self.mouse_buffer = event.pos()
        mouse_delta = event.pos() - self.mouse_buffer

        if Qt.MiddleButton == event.buttons() and Qt.NoModifier == event.modifiers():
            self.camera.pan(-mouse_delta.x()/screen_width, -mouse_delta.y()/screen_height)
            self.update()

        if Qt.LeftButton == event.buttons() and Qt.AltModifier == event.modifiers():
            self.camera.pan(-mouse_delta.x()/screen_width, -mouse_delta.y()/screen_height)
            self.update()

        if Qt.LeftButton == event.buttons() and Qt.NoModifier == event.modifiers():
            self.camera.orbit(-mouse_delta.x()*0.006, -mouse_delta.y()*0.006)
            self.update()
        self.mouse_buffer = event.pos()

    def mouseReleaseEvent(self, event:QMouseEvent):
        self.mouse_buffer = event.pos()

    def wheelEvent(self, event:QWheelEvent):
        self.camera.dolly(event.angleDelta().y()/360.0*self.camera.get_target_distance()*0.5)
        self.update()
        
    def setImage(self, img:np.ndarray, internalformat=None):
        assert(self.isValid()) # opengg must be initalized at this point. call widget.show before setting the image

        image_aspect = img.shape[1]/ img.shape[0]
        self.model = glm.scale(glm.mat4(1), glm.vec3(image_aspect, 1, 1))

        tex = make_texture(img)
        
        self.setTexture(tex)

    def setTexture(self, tex: int):
        if self.tex is not None: glDeleteTextures([self.tex]) # Delete previous texture
        self.tex = tex
        self.update()




def main():
    # Create UV image gradient
    U, V = np.mgrid[0:255:720j, 0:255:1280j].astype(np.uint8)
    W = np.full(shape=U.shape, fill_value=0, dtype=np.uint8)
    UVW = np.dstack([U, V, W])

    #QApplication.setAttribute(Qt.AA_UseDesktopOpenGL)
    a = QApplication(sys.argv)
    window = GLViewer()
    window.show()
    window.setImage(UVW)
    sys.exit(a.exec_())

if __name__ == "__main__":
    main()