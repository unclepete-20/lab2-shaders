from bmp_renderer import *
from lib import *

pi =3.1416
                        

r = Render(500, 500)
r.glColor(color_select(0, 0, 0))
r.lookAt(V3(-1,0,5),V3(0,0,0),V3(0,1,0))

#creeper
scale_factor = (0.5,0.5,1)
translate_factor = (0, 0, 0)
rotate_factor = (0,0,0)
r.active_texture = Texture("creeper.bmp")
r.active_shader = r.shader
r.render_obj('Creeper.obj',translate_factor,scale_factor,rotate_factor)
r.draw('TRIANGLES') 


r.write('sr5.bmp')