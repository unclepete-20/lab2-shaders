import struct
from Vector import *

# Constants for BMP files
FILE_SIZE = (54)
PIXEL_COUNT = 3
PLANE = 1
BITS_PER_PIXEL = 24
DIB_HEADER = 40

def char(c):
    # 1 byte
    return struct.pack('=c',c.encode('ascii'))

def word(w):
    # 2  bytes
    return struct.pack('=h',w)

def dword(d):
    #4 bytes
    return struct.pack('=l', d)

def cross(v1,v2):
    return (
        v1.y * v2.z - v1.z * v2.y,
        v1.z * v2.x - v1.x * v2.z,
        v1.x * v2.y - v1.y * v2.x
    )

def bounding_box(A,B,C):
    coors = [(A.x, A.y),(B.x, B.y),(C.x, C.y)]

    xmin = 999999
    xmax = -999999
    ymin = 999999
    ymax = -999999

    for (x,y) in coors:
        if x < xmin:
            xmin = x
        if x > xmax:
            xmax = x
        if y < ymin:
            ymin = y
        if y > ymax:
            ymax = y
    return V3(xmin, ymin), V3(xmax, ymax)

def color_select(r, g, b):
    return bytes([round(b),round(g),round(r)])


def barycentric(A,B,C,P):
    
    cx,cy,cz = cross(
        V3(B.x - A.x, C.x - A.x, A.x - P.x),
        V3(B.y - A.y, C.y - A.y, A.y - P.y)
    )
    if cz == 0:
        return(-1,-1,-1)
    u = cx / cz
    v = cy / cz
    w = 1 - (u + v) 

    return (w, v, u)

def glFinish(filename, width, height, framebuffer):
    # Constants for BMP files
    file_size = (54)
    pixel_count = 3
    plane = 1
    bits_per_pixel = 24
    dib_header = 40
    
    file = open(filename, 'bw')
    # Header
    file.write(char('B'))
    file.write(char('M'))

    # File size
    file.write(dword(file_size + height * width * pixel_count))
    file.write(word(0))
    file.write(word(0))
    file.write(dword(file_size))

    # Info Header
    file.write(dword(dib_header))
    file.write(dword(width))
    file.write(dword(height))
    file.write(word(plane))
    file.write(word(bits_per_pixel))
    file.write(dword(0))
    file.write(dword(width * height * pixel_count))
    file.write(dword(0))
    file.write(dword(0))
    file.write(dword(0))
    file.write(dword(0))

    #PIXEL DATA
    try:
        for y in range(height):
            for x in range(width):
                file.write(framebuffer[y][x])
    except:
        pass

    file.close()

def glLine(x0,y0,x1,y1):        
        dy = abs(y1-y0)
        dx = abs(x1-x0)

        steep = dy > dx

        if steep:
            x0,y0 = y0,x0
            x1,y1 = y1,x1

        if  x0>x1:
            x0,x1 = x1,x0
            y0,y1 = y1,y0

        dy = abs(y1-y0)
        dx = x1-x0

        offset = 0
        threshold = dx
        y = y0

        points = []

        for x in range(x0, x1 + 1):
            if steep:
                points.append((x, y))
            else:
                points.append((y, x))
            offset += dy * 2
            if offset >= threshold:
                y +=1 if y0 < y1 else -1
                threshold += dx * 2
        return points

def createMatrix(dataList):
    matrix = []
    for m in range(len(dataList)):
        Listrow = []
        for k in range(len(dataList[0])):
            Listrow.append(dataList[len(dataList)* m + k])
        matrix.append(Listrow)

    return matrix