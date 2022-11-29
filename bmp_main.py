from bmp_renderer import *
from lib import *
from Texture import *
                        
'''
LAB 2: SHADERS
'''
# Background texture
frame = Render(1024, 1024)
frame.lookAt(V3(0, 1, 1),V3(0, 1, 0),V3(0, 1, 0))
frame.active_texture = Texture('space.bmp')
frame.framebuffer = frame.active_texture.pixels
frame.active_shader = frame.shader


# Neptune and moons
scale_factor = (1, 1, 0)
translate_factor = (0, 1, 0)
rotate_factor = (0, 0, 0)
frame.active_shader = frame.mars
frame.render_obj('sphere.obj', translate_factor,scale_factor, rotate_factor)
frame.draw('TRIANGLES')

scale_factor = (0.2, 0.2, 0)
translate_factor = (-0.4, 1.4, 0.1)
rotate_factor = (0, 0, 0)
frame.active_shader = frame.phobos
frame.render_obj('sphere.obj', translate_factor,scale_factor, rotate_factor)
frame.draw('TRIANGLES')

scale_factor = (0.2, 0.2, 0)
translate_factor = (0.5, 0.5, -0.05)
rotate_factor = (0, 0, 0)
frame.active_shader = frame.deimos
frame.render_obj('sphere.obj', translate_factor,scale_factor, rotate_factor)
frame.draw('TRIANGLES') 

frame.write('mars_shader.bmp')


# Medium shot
#r.lookAt(V3(0, 0, 10),V3(0, 0.2, -3),V3(0, 1, 0))

# Low angle
#r.lookAt(V3(0, -10, 10),V3(0, 0, 0),V3(0, 1, 0))

# High angle
#r.lookAt(V3(0, 10, 10),V3(0, 0, 0),V3(0, 1, 0))

# Dutch angle
#r.lookAt(V3(1, 2, 10),V3(0, 0, -2),V3(1, 1.5, 2))

# Medium shot render
#r.write('medium_shot.bmp')

# Low angle render
#r.write('low_angle.bmp')

# High angle render
#r.write('high_angle.bmp')

# Dutch angle render
#r.write('dutch_angle.bmp')