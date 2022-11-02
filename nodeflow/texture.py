

from dataclasses import dataclass
from OpenGL.GL import *

import numpy as np
from core import Operator, Constant


@dataclass(frozen=False)
class Texture:
    tex:int
    def __init__(self, tex:int=-1):
        self.tex = int(tex)
        if self.tex == -1:
            self.tex = int(glGenTextures( 1 ))
            print(self.tex)


    def __del__(self):
        if self.tex>0 and glIsTexture(self.tex):
            print("delete texture:", self.tex, type(self.tex))
            glDeleteTextures(1, [self.tex])


class ToTexture(Operator):
    def __init__(self, image: Operator):
        super().__init__(image)

    def __call__(self, img:np.ndarray):
        # GLFormat from numpy shape
        height, width, channels = img.shape
        if channels==1:
            glformat = GL_RED
        elif channels==2:
            glformat = GL_RG
        elif channels==3:
            glformat = GL_RGB
        elif channels==4:
            glformat=GL_RGBA
        else:
            raise NotImplementedError

        # GLType from numpy dtype
        if img.dtype == np.uint8:
            gltype = GL_UNSIGNED_BYTE
        elif img.dtype == np.float16:
            gltype = GL_HALF_FLOAT
        elif img.dtype == np.float32:
            gltype = GL_FLOAT
        else:
            raise NotImplementedError

        # Match internal format
        internalformat = None
        if internalformat is None: 
            if glformat is GL_RED:
                if gltype is GL_UNSIGNED_BYTE: internalformat=GL_R8
                elif gltype is GL_HALF_FLOAT: internalformat=GL_R16F
                elif gltype is GL_FLOAT: internalformat=GL_R32F
                else: raise NotImplementedError
            elif glformat is GL_RG:
                if gltype is GL_UNSIGNED_BYTE: internalformat=GL_RG8
                elif gltype is GL_HALF_FLOAT: internalformat=GL_RG16F
                elif gltype is GL_FLOAT: internalformat=GL_RG32F
                else: raise NotImplementedError
            elif glformat is GL_RGB:
                if gltype is GL_UNSIGNED_BYTE: internalformat=GL_RGB8
                elif gltype is GL_HALF_FLOAT: internalformat=GL_RGB16F
                elif gltype is GL_FLOAT: internalformat=GL_RGB32F
                else: raise NotImplementedError
            elif glformat is GL_RGBA:
                if gltype is GL_UNSIGNED_BYTE: internalformat=GL_RGBA8
                elif gltype is GL_HALF_FLOAT: internalformat=GL_RGBA16F
                elif gltype is GL_FLOAT: internalformat=GL_RGBA32F
                else: raise NotImplementedError
            else:
                raise NotImplementedError

        # Update texture
        tex = glGenTextures( 1 )
        glBindTexture(GL_TEXTURE_2D, tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER) # parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexImage2D(GL_TEXTURE_2D, 0, internalformat, width, height, 0, glformat, gltype, img) # to GPU
        # glGenerateMipmap(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, 0)

        return Texture(tex) # take ownership, delete if unused

        
class ApplyShader(Operator):
    def __init__(self, input_texture:Operator, fragment_code: str):
        super().__init__(input_texture)
        self.viewport = (0,0,512,512)

        self.init_texture()
        self.init_fbo()
        self.fragment_code = fragment_code
        self.init_shaders()
        self.init_quad()

    def init_texture(self):
        self.tex = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.tex)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_BORDER) # parameters
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_BORDER)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)

        internalformat = GL_RGBA32F
        glTexImage2D(GL_TEXTURE_2D, 0, internalformat, 512,512, 0, GL_RGBA, GL_FLOAT, None)

        glBindTexture(GL_TEXTURE_2D, 0)

    def init_fbo(self):
        self.fbo = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.tex, 0)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("ERROR::FRAMEBUFFER:: Framebuffer is not complete!")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def init_shaders(self):
        """compile shaders and link program"""

        vertex_code = """
            #version 330 core

            in vec3 aPos;
            in vec2 aUV;

            out vec2 vUV;

            void main()
            {
                vUV = aUV;
                gl_Position = vec4(aPos, 1.0);
            }
        """
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_code)
        glCompileShader(vertex_shader)
        if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
            error_msg = glGetShaderInfoLog(vertex_shader)
            raise RuntimeError(f"Shader compilation error: {error_msg}") 

        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, self.fragment_code)
        glCompileShader(fragment_shader)
        if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
            error_msg = glGetShaderInfoLog(fragment_shader)
            raise RuntimeError(f"Shader compilation error: {error_msg}")

        # Make program
        program = glCreateProgram()
        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)

        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            error_msg = glGetShaderInfoLog(fragment_shader)
            raise RuntimeError(f"Program linking error: {error_msg}")

        self.program = program

        # Delete shaders
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        # Default uniform values
        glUseProgram(self.program)
        glUseProgram(0)

    def init_quad(self):
        """Create image plane"""
        # Geometry data
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

        # Geometry buffers
        # VBO
        pos_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, pos_vbo)
        glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        uv_vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, uv_vbo)
        glBufferData(GL_ARRAY_BUFFER, uvs.nbytes, uvs, GL_DYNAMIC_DRAW)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # EBO
        ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        self.ebo = ebo

        # VAO
        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)
        loc = glGetAttribLocation(self.program, "aPos")
        if loc >=0:
            glEnableVertexAttribArray(loc)
            glBindBuffer(GL_ARRAY_BUFFER, pos_vbo)
            glVertexAttribPointer(loc, 3, GL_FLOAT, False, positions.strides[0], ctypes.c_void_p(0))
        else:
             print("aPos attribute is not used")

        loc = glGetAttribLocation(self.program, "aUV")
        if loc >=0:
            glEnableVertexAttribArray(loc)
            glBindBuffer(GL_ARRAY_BUFFER, uv_vbo)
            glVertexAttribPointer(loc, 2, GL_FLOAT, False, uvs.strides[0], ctypes.c_void_p(0))
        else:
             print("aUV attribute is not used")
        self.vao = vao


    def __del__(self):
        if self.tex is not None and glIsTexture(self.tex):
            glDeleteTextures(1, [self.tex]) # the error when exit probably occures because the opengl context was already cleaned up
        if self.fbo is not None and glIsFramebuffer(self.fbo):
            glDeleteFramebuffers(1, [self.fbo])
        if self.program is not None and glIsProgram(self.program):
            glDeleteProgram(self.program)

    def __call__(self, input_texture: Texture)->Texture:
        # Begin render to texture
        glUseProgram(self.program)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glViewport(*self.viewport)

        # Draw on texture
        glBindTexture(GL_TEXTURE_2D, input_texture.tex)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, ctypes.c_void_p(0))
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindVertexArray(0)
        glBindTexture(GL_TEXTURE_2D, 0)

        # End render to Texture
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        return Texture(self.tex)


if __name__ == "__main__":
    import sys
    from PySide2.QtWidgets import QApplication
    from gui.glviewer import GLViewer

    from pathlib import Path
    print("CWD:", Path.cwd())

    app = QApplication(sys.argv)
    viewer = GLViewer()
    viewer.show()
    
    #=========================
    from core import evaluate
    from image import Read, Ramp

    # Graph
    ramp = Ramp((512,512))

    filename = Constant(str(Path.cwd() / Path("tests/SMPTE_colorbars/SMPTE_colorbars_00001.jpg")))
    read = Read(filename)
    to_tex = ToTexture(read)
    shd = ApplyShader(to_tex, """
        #version 330 core

        in vec2 vUV;
        uniform sampler2D textureMap;
        out vec4 fragColor;
        void main()
        {
            vec4 tex = texture(textureMap, vUV);
            fragColor = vec4(tex.rgb*0.3, 1.0);
        }
    """)
    out = shd

    # display
    result = evaluate(out)
    viewer.setTexture(result.tex)
    sys.exit(app.exec_())
