from bmp_renderer import *
from lib import *

pi =3.1416
                        

r = Render(500, 500)

# Medium shot
r.lookAt(V3(0, 0, 10),V3(0, 0.2, -3),V3(0, 1, 0))

# Low angle
#r.lookAt(V3(0, -10, 10),V3(0, 0, 0),V3(0, 1, 0))

# High angle
#r.lookAt(V3(0, 10, 10),V3(0, 0, 0),V3(0, 1, 0))

# Dutch angle
#r.lookAt(V3(1, 2, 10),V3(0, 0, -2),V3(1, 1.5, 2))

#creeper
scale_factor = (0.5, 0.5, 1)
translate_factor = (0, 0, 0)
rotate_factor = (0, 0.2, 0)
r.active_texture = Texture("creeper.bmp")
r.active_shader = r.shader
r.render_obj('Creeper.obj', translate_factor,scale_factor, rotate_factor)
r.draw('TRIANGLES') 

# Medium shot render
r.write('medium_shot.bmp')

# Low angle render
#r.write('low_angle.bmp')

# High angle render
#r.write('high_angle.bmp')

# Dutch angle render
#r.write('dutch_angle.bmp')