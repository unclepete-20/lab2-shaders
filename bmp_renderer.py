from Texture import *
from Vector import *
from Obj import *
from lib import *
from Matrix import *
from math import *
import random

class Render(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.clearColor = color_select(255, 255, 255)
        # Initializes the window on create
        self.glCreateWindow()
        self.vertex_buffer_object = []
        self.active_vertex_array = []
        self.active_texture = None
        self.active_shader = None
        self.Light = V3(0, 0, 1)
        self.Model = None
        self.View = None
        
        

    def loadModelMatrix(self,translate =(0,0,0), scale=(1,1,1), rotate = (0,0,0)):
        translate = V3(*translate)
        scale = V3(*scale)
        rotate = V3(*rotate)

        translation_matrix = Matrix([
            [1,0,0,translate.x],
            [0,1,0,translate.y],
            [0,0,1,translate.z],
            [0,0,0,1],
        ])

        scale_matrix = Matrix([
            [scale.x,0,0,0],
            [0,scale.y,0,0],
            [0,0,scale.z,0],
            [0,0,0,1],
        ])
        
        a = rotate.x
        rotation_x = Matrix([
            [1,0,0,0],
            [0,cos(a),-sin(a),0],
            [0,sin(a),cos(a),0],
            [0,0,0,1],
        ])
        a = rotate.y
        rotation_y = Matrix([
            [cos(a),0,sin(a),0],
            [0,1,0,0],
            [-sin(a),0,cos(a),0],
            [0,0,0,1],
        ])
        a = rotate.z
        rotation_z = Matrix([
            [cos(a),-sin(a),0,0],
            [sin(a),cos(a),0,0],
            [0,0,1,0],
            [0,0,0,1],
        ])
     
        rotation_matrix = rotation_x @ rotation_y @ rotation_z
        
        self.Model = translation_matrix @ rotation_matrix @ scale_matrix
        

    def write(self, filename):
        glFinish(filename, self.width, self.height, self.framebuffer)

    def lookAt(self, eye, center, up):
        z = (eye - center).norm()
        x = (up * z).norm()
        y = (z * x).norm()

        self.loadViewMatrix(x,y,z,center)
        self.loadProjectionMatrix(eye,center)
        self.loadViewportMatrix()

    def loadViewMatrix(self, x, y, z, center):
        Mi = Matrix([
            [x.x,x.y,x.z,0],
            [y.x,y.y,y.z,0],
            [z.x,z.y,z.z,0],
            [0,0,0,1]
        ])

        Op = Matrix([
            [1,0,0,-center.x],
            [0,1,0,-center.y],
            [0,0,1,-center.z],
            [0,0,0,1]
        ])

        self.View = Mi @ Op
        
        
    def loadProjectionMatrix(self,eye,center):
        coeff = -1 / (eye.__length__() - center.__length__())
        self.Projection = Matrix([
            [1,0,0,0],
            [0,1,0,0],
            [0,0,1,0],
            [0,0,coeff,1],
        ])

    def loadViewportMatrix(self):
        x = 0
        y = 0
        w = self.width / 2
        h = self.height / 2

        self.Viewport = Matrix([
            [w,0,0,x+w],
            [0,h,0,y+h],
            [0,0,128,128],
            [0,0,0,1],
        ])


    def glCreateWindow(self):
        self.framebuffer = [
            [self.clearColor for x in range(self.width)]
            for y in range(self.height)
        ]
        self.zBuffer = [
            [-9999 for x in range(self.width)]
            for y in range(self.height)
        ]
        
    def shader(self, **kwargs):
        w,u,v = kwargs['bar']
        Light = kwargs['light']
        A,B,C = kwargs['vertices']
        tA, tB, tC = kwargs['texture_coordinates']
        nA, nB, nC = kwargs['normals']
        
        iA = nA.norm() @ Light.norm()    
        iB = nB.norm() @ Light.norm()   
        iC = nC.norm() @ Light.norm()

        i = iA * w + iB * u + iC * v   
         

        if self.active_texture:
            tx = tA.x * w +tB.x * u + tC.x * v
            ty = tA.y * w +tB.y * u + tC.y * v
            

            return self.active_texture.get_color_with_intensity(tx, ty, i)

    def glPoint(self, x, y):
        if (0 < x < self.width and 0 < y < self.height):
            self.framebuffer[x][y] = self.clearColor

    def glColor(self, c):
        self.clearColor = c

    def line(self, p1,p2):
        x0 = round(p1.x)
        y0 = round(p1.y)
        x1 = round(p2.x)
        y1 = round(p2.y)
        
        points = glLine(x0,y0,x1,y1)
        for point in points:
            self.glPoint(*point)

    def triangle_babycenter(self):
        A = next(self.active_vertex_array)
        
        B = next(self.active_vertex_array)
        
        C = next(self.active_vertex_array)
        

        if self.active_texture:
            tA = next(self.active_vertex_array)
            tB = next(self.active_vertex_array)
            tC = next(self.active_vertex_array)
            
        if self.active_shader:
            nA = next(self.active_vertex_array)
            nB = next(self.active_vertex_array)
            nC = next(self.active_vertex_array)
            

        min,max = bounding_box(A,B,C)
        min.round()
        max.round()
        
        for x in range(min.x, max.x + 1):
            for y in range(min.y, max.y + 1):
                w, v, u = barycentric(A, B, C, V3(x,y))

                if (w < 0 or v < 0 or u < 0):
                    continue

                z = A.z * w + B.z * v + C.z * u
                if (x >= 0 and
                    y >= 0 and
                    x < len(self.zBuffer) and  
                    y < len(self.zBuffer[0]) and 
                    self.zBuffer[x][y] < z):
                    self.zBuffer[x][y] = z
                    self.clearColor = self.active_shader(
                        bar = (w, u, v),
                        vertices=(A, B, C),
                        texture_coordinates = (tA,tB,tC),
                        normals = (nA, nB, nC),
                        light = self.Light,
                        coorinates = (x, y)
                        )
              
                    self.glPoint(y, x)

    def triangle_wireframe(self):
        A = next(self.active_vertex_array)
        B = next(self.active_vertex_array)
        C = next(self.active_vertex_array)

        if self.active_texture:
            tA = next(self.active_vertex_array)
            tB = next(self.active_vertex_array)
            tC = next(self.active_vertex_array)
        
        self.line(A, B)
        self.line(B, C)
        self.line(C, A)
    
    def transform_vertex(self, vertex):
        augmented_vertex = Matrix([
            vertex[0],
            vertex[1],
            vertex[2],
            1
        ])

        transformed_vertex =  self.Viewport @ self.Projection @ self.View @ self.Model @ augmented_vertex 
        
        transformed_vertex = V3(transformed_vertex)

        return V3(
            transformed_vertex.x/transformed_vertex.w,
            transformed_vertex.y/transformed_vertex.w,
            transformed_vertex.z/transformed_vertex.w,
        )

    
    def render_obj(self, obj, translate=(0, 0, 0), scale=(1, 1, 1), rotate=(0, 0, 0)):
        
        self.loadModelMatrix(translate, scale, rotate)
        model = Obj(obj)

        for face in model.faces:
            if len(face) == 4:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1
                f4 = face[3][0] - 1
                v1 = self.transform_vertex(model.vertices[f1])
                v2 = self.transform_vertex(model.vertices[f2])
                v3 = self.transform_vertex(model.vertices[f3])
                v4 = self.transform_vertex(model.vertices[f4])
                
                
                self.vertex_buffer_object.append(v1)
                self.vertex_buffer_object.append(v2)
                self.vertex_buffer_object.append(v3)
                
                if self.active_texture:

                    ft1 = face[0][1] - 1
                    ft2 = face[1][1] - 1
                    ft3 = face[2][1] - 1

                    vt1 = V3(*model.tvertices[ft1])
                    vt2 = V3(*model.tvertices[ft2])
                    vt3 = V3(*model.tvertices[ft3])

                    self.vertex_buffer_object.append(vt1)
                    self.vertex_buffer_object.append(vt2)
                    self.vertex_buffer_object.append(vt3)

                try:
                    fn1 = face[0][2] - 1
                    fn2 = face[1][2] - 1
                    fn3 = face[2][2] - 1

                    vn1 = V3(*model.nvertices[fn1])
                    vn2 = V3(*model.nvertices[fn2])
                    vn3 = V3(*model.nvertices[fn3])
                
                    self.vertex_buffer_object.append(vn1)
                    self.vertex_buffer_object.append(vn2)
                    self.vertex_buffer_object.append(vn3)
                except:
                    pass
                
                self.vertex_buffer_object.append(v1)
                self.vertex_buffer_object.append(v3)
                self.vertex_buffer_object.append(v4)

                if self.active_texture:

                    ft1 = face[0][1] - 1
                    ft3 = face[2][1] - 1
                    ft4 = face[3][1] - 1

                    vt1 = V3(*model.tvertices[ft1])
                    vt3 = V3(*model.tvertices[ft3])
                    vt4 = V3(*model.tvertices[ft4])

                    self.vertex_buffer_object.append(vt1)
                    self.vertex_buffer_object.append(vt3)
                    self.vertex_buffer_object.append(vt4)
                try:
                    fn1 = face[0][2] - 1
                    fn3 = face[2][2] - 1
                    fn4 = face[3][2] - 1

                    vn1 = V3(*model.nvertices[fn1])
                    vn3 = V3(*model.nvertices[fn3])
                    vn4 = V3(*model.nvertices[fn4])
                
                    self.vertex_buffer_object.append(vn1)
                    self.vertex_buffer_object.append(vn3)
                    self.vertex_buffer_object.append(vn4)
                except:
                    pass

            if len(face) == 3:
                f1 = face[0][0] - 1
                f2 = face[1][0] - 1
                f3 = face[2][0] - 1

                v1 = self.transform_vertex(model.vertices[f1])
                v2 = self.transform_vertex(model.vertices[f2])
                v3 = self.transform_vertex(model.vertices[f3])

                self.vertex_buffer_object.append(v1)
                self.vertex_buffer_object.append(v2)
                self.vertex_buffer_object.append(v3)

                if self.active_texture:

                    ft1 = face[0][1] - 1
                    ft2 = face[1][1] - 1
                    ft3 = face[2][1] - 1

                    vt1 = V3(*model.tvertices[ft1])
                    vt2 = V3(*model.tvertices[ft2])
                    vt3 = V3(*model.tvertices[ft3])

                    self.vertex_buffer_object.append(vt1)
                    self.vertex_buffer_object.append(vt2)
                    self.vertex_buffer_object.append(vt3)
                
                try:
                    fn1 = face[0][2] - 1
                    fn2 = face[1][2] - 1
                    fn3 = face[2][2] - 1

                    vn1 = V3(*model.nvertices[fn1])
                    vn2 = V3(*model.nvertices[fn2])
                    vn3 = V3(*model.nvertices[fn3])
                
                    self.vertex_buffer_object.append(vn1)
                    self.vertex_buffer_object.append(vn2)
                    self.vertex_buffer_object.append(vn3)
                except:
                    pass

        self.active_vertex_array = iter(self.vertex_buffer_object)

    def draw(self,polygon):
        if polygon == 'TRIANGLES':
            try:
                while True:
                    self.triangle_babycenter()
            except StopIteration:
                print("FINISHED DRAWING TRIANGLE")
        if polygon == 'WIREFRAME':
            try:
                while True:
                    self.triangle_wireframe()
            except StopIteration:
                print("FINISHED DRAWING WIREFRAME") 
    
    def mars(self, **kwargs):
        x, y = kwargs['coorinates']
        
        if y > 760 - random.randint(0, 50) and x > 500 - random.randint(0, 50) and x < 550 + random.randint(0, 50):
            return color_select(75, 75, 75)
        elif x < 500 + random.randint(0, 50):
            if x > 350 - random.randint(0, 50) and x < 450 + random.randint(0, 50):
                if 500 - random.randint(0, 50) < y < 450 + random.randint(0, 50):
                    return color_select(85, 85, 85)
                elif 400 - random.randint(0, 50) < x < 450 + random.randint(0, 50):
                    if 450 - random.randint(0, 50) < y < 450 + random.randint(0, 50):
                        return color_select(130, 130, 130)
                if x > 350 - random.randint(0, 50):
                    if 700 - random.randint(0, 50) < y < 650 + random.randint(0, 50):
                        return color_select(85, 84, 65)
            return color_select(150, 84, 61)
        elif y < 300 + random.randint(0, 50) and x > 500 - random.randint(0, 50) and x < 550 + random.randint(0, 50):
            return color_select(75, 75, 75)
            
        elif x >= 500:
            i = (x - 450) * 0.3
            r = 150 - i 
            g = 84 - i
            b = 61 - i
            
            if 600 - random.randint(0, 50) < x < 600 + random.randint(0, 50):
                if 500 - random.randint(0, 50)< y < 550 + random.randint(0, 50):
                    return color_select(35, 13, 6)
            if 680 - random.randint(0, 50) < x < 700 + random.randint(0, 50):
                if 650 - random.randint(0, 50)< y < 650 + random.randint(0, 50):
                    return color_select(35, 13, 6)
                
            if 0 <= r <= 255:
                pass
            else:
                r = 0
            if 0 <= g <= 255:
                pass
            else:
                g = 0
            if 0 <= b<= 255:
                pass
            else:
                b = 0
            return color_select(r, g, b)
    
    def phobos(self, **kwargs):
        x, y = kwargs['coorinates']
        
        if y > 200 - random.randint(0, 50) and x > 500 - random.randint(0, 50) and x < 550 + random.randint(0, 50):
            return color_select(150, 128, 128)
        elif x < 500 + random.randint(0, 50):
            if x > 300- random.randint(0, 50) and x < 450 + random.randint(0, 50):
                if 450 - random.randint(0, 50) < y < 450 + random.randint(0, 50):
                    return color_select(128, 128, 128)
                elif 400 - random.randint(0, 50) < x < 450 + random.randint(0, 50):
                    if 400 - random.randint(0, 50) < y < 450 + random.randint(0, 50):
                        return color_select(80, 80, 80)
                if x > 350 - random.randint(0, 50):
                    if 600 - random.randint(0, 50) < y < 650 + random.randint(0, 50):
                        return color_select(128, 128, 128)
            return color_select(128, 128, 128)
        elif y < 250 + random.randint(0, 50) and x > 500 - random.randint(0, 50) and x < 550 + random.randint(0, 50):
            return color_select(80, 128, 128)
            
        elif x >= 500:
            i = (x - 450) * 0.3
            r = 80 - i 
            g = 90 - i
            b = 128 - i
            
            if 500 - random.randint(0, 50) < x < 600 + random.randint(0, 50):
                if 400 - random.randint(0, 50)< y < 550 + random.randint(0, 50):
                    return color_select(200, 90, 128)
            if 680 - random.randint(0, 50) < x < 700 + random.randint(0, 50):
                if 400 - random.randint(0, 50)< y < 650 + random.randint(0, 50):
                    return color_select(128, 128, 128)
                
            if 0 <= r <= 255:
                pass
            else:
                r = 0
            if 0 <= g <= 255:
                pass
            else:
                g = 0
            if 0 <= b<= 255:
                pass
            else:
                b = 0
            return color_select(r, g, b)
    
    def deimos(self, **kwargs):
        x, y = kwargs['coorinates']
        
        if y > 760 - random.randint(0, 50) and x > 500 - random.randint(0, 50) and x < 550 + random.randint(0, 50):
            return color_select(150, 75, 0)
        elif x < 500 + random.randint(0, 50):
            if x > 300- random.randint(0, 50) and x < 450 + random.randint(0, 50):
                if 450 - random.randint(0, 50) < y < 450 + random.randint(0, 50):
                    return color_select(150, 75, 0)
                elif 400 - random.randint(0, 50) < x < 450 + random.randint(0, 50):
                    if 400 - random.randint(0, 50) < y < 450 + random.randint(0, 50):
                        return color_select(150, 75, 0)
                if x > 350 - random.randint(0, 50):
                    if 600 - random.randint(0, 50) < y < 650 + random.randint(0, 50):
                        return color_select(150, 75, 0)
            return color_select(150, 75, 0)
        elif y < 250 + random.randint(0, 50) and x > 500 - random.randint(0, 50) and x < 550 + random.randint(0, 50):
            return color_select(150, 75, 0)
            
        elif x >= 450:
            i = (x - 450) * 0.2
            r = 150 - i 
            g = 75 - i
            b = 1 - i
            
            if 500 - random.randint(0, 50) < x < 600 + random.randint(0, 50):
                if 400 - random.randint(0, 50)< y < 550 + random.randint(0, 50):
                    return color_select(150, 75, 0)
            if 680 - random.randint(0, 50) < x < 700 + random.randint(0, 50):
                if 400 - random.randint(0, 50)< y < 650 + random.randint(0, 50):
                    return color_select(150, 75, 0)
                
            if 0 <= r <= 255:
                pass
            else:
                r = 0
            if 0 <= g <= 255:
                pass
            else:
                g = 0
            if 0 <= b<= 255:
                pass
            else:
                b = 0
            return color_select(r, g, b)       
