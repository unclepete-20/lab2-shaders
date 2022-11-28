import struct
from lib import *

class Texture:
    def __init__(self,path):
        self.path = path
        self.read()

    def read(self):
        with open(self.path, "rb") as image:
            image.seek(2 + 4 + 2 + 2)
            header_size = struct.unpack("=l",image.read(4))[0]
            image.seek(2 + 4 + 2 + 2 + 4 + 4)
            self.width = struct.unpack("=l",image.read(4))[0]
            self.height = struct.unpack("=l",image.read(4))[0]

            image.seek(header_size)

            self.pixels = []
            for y in range(self.height):
                self.pixels.append([])
                for x in range(self.width):
                    b = ord(image.read(1))
                    g = ord(image.read(1))
                    r = ord(image.read(1))
                    self.pixels[y].append(
                        color_select(r,g,b)
                    )

    def get_color(self,tx,ty):
        x = round(tx * self.width)
        y = round(ty * self.height)

        return self.pixels[y][x]

    def get_color_with_intensity(self,tx,ty,intensity):
        x = round(tx * self.width)
        y = round(ty * self.height)
        try:
            b = round(self.pixels[y][x][0] * intensity)
        except:
            b = 255 * intensity
        try:
            g = round(self.pixels[y][x][1] * intensity) 
        except:
            g = 255 * intensity
        try:
            r = round(self.pixels[y][x][2] * intensity)
        except:
            r = 255 * intensity
        return color_select(
            max(min(r,255),0),
            max(min(g,255),0),
            max(min(b,255),0)
            )

