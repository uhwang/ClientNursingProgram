# Vector Graphic Library (VGL) for Python
#
# color.py
#
# 2020-2-12 Ver 0.1
#
# Author: Uisang Hwang
# Email : uhwangtx@gmail.com
#
def get_rgb(c): return c.r/255., c.r/255., c.r/255.
def get_style(c): return "#%02x%02x%02x"%(c.r, c.g, c.b)
def normalize(c): return Color(c.r/255., c.g/255., c.b/255.)

class Color():
    def __init__(self,r=255,g=255,b=255):
        #self.conv(col)
        self.r = r
        self.g = g
        self.b = b

    def __eq__(self, c):
        return self.r == c.r and self.g == c.g and self.b == c.b

    def __str__(self):
        format = "%3.3f, %03.3f, %03.3f" if isinstance(self.r, float) else\
                 "%03d, %03d, %03d"
        return format%(self.r, self.g, self.b)

    def css(self):
        return f'#{self.r:02x}{self.g:02x}{self.b:02x}'
        
    def get_tuple(self) : return (self.r, self.g, self.b)

BLACK   = Color(0  ,  0,  0)
WHITE   = Color(255,255,255)
RED     = Color(255,  0,  0)
GREEN   = Color(0  ,255,  0)
BLUE    = Color(0  ,  0,255)
YELLOW  = Color(255,255,  0)
MAGENTA = Color(255,  0,255)
CYAN    = Color(0  ,255,255)
PURPLE  = Color(255,  0,255)
CUSTOM1 = Color(255,127,  0)
CUSTOM2 = Color(127,255,  0)
CUSTOM3 = Color(0  ,255,127)
CUSTOM4 = Color(127,  0,255)
CUSTOM5 = Color(255,  0,127)
GRAY10  = Color( 10, 10, 10)
GRAY20  = Color( 20, 20, 20)
GRAY30  = Color( 30, 30, 30)
GRAY40  = Color( 40, 40, 40)
GRAY50  = Color( 50, 50, 50)
GRAY60  = Color( 60, 60, 60)
GRAY70  = Color( 70, 70, 70)
GRAY80  = Color( 80, 80, 80)
GRAY90  = Color( 90, 90, 90)
GRAY100 = Color(100,100,100)

color_name = "b,w,r,g,b,y,m,c,p,c1,c2,c3,c4,c5,g10,g20,g30,g40,g50,g60,g70,g80,g90,g100"

default_color = {
"k" : BLACK   ,
"w" : WHITE   ,
"r" : RED     ,
"g" : GREEN   ,
"b" : BLUE    ,
"y" : YELLOW  ,
"m" : MAGENTA ,
"c" : CYAN    ,
"p" : PURPLE  ,
"c1" : CUSTOM1 ,
"c2" : CUSTOM2 ,
"c3" : CUSTOM3 ,
"c4" : CUSTOM4 ,
"c5" : CUSTOM5 ,
"g10" : GRAY10  ,
"g20" : GRAY20  ,
"g30" : GRAY30  ,
"g40" : GRAY40  ,
"g50" : GRAY50  ,
"g60" : GRAY60  ,
"g70" : GRAY70  ,
"g80" : GRAY80  ,
"g90" : GRAY90  ,
"g100" : GRAY100
}

Gray = lambda p: Color(p,p,p)

def create_gray_table(order, g1=0, g2=100):
    return [Color(i,i,i) for i in range(g1, g2, int(100/order))]

# SVG Color Codes
# https://johndecember.com/html/spec/colorsvghex.html


agg_color = lambda x: (0,x[2],x[1],x[0])
get_gray  = lambda x: (int(x*255), int(x*255), int(x*255))

# level : 0~1
_gray = lambda level: Color(int(level*255), int(level*255), int(level*255))

#class rgb():
#    def __init__(self,col=WHITE):
#        self.conv(col)
#
#    def conv(self,col):
#        self.r, self.g, self.b = get_rgb(col)
#
#    def __str__(self):
#        return "RGB: %03d, %03d, %03d"%(self.r, self.g, self.b)

#inv_255 = 0.00392156862745

def hsv(H, S, V):
	import math
	I = 0.0
	F = 0.0
	P = 0.0
	Q = 0.0
	T = 0.0
	R1 = 0.0
	G1 = 0.0
	B1 = 0.0

	if S == 0:
		if H <= 0 or H > 360 :
			return Color(int(V*255),int(V*255),int(V*255))

	if H==360: H=0

	H = H/60;
	I = math.floor(H)
	F = H-I
	P = V*(1-S)
	Q = V*(1-S*F)
	T = V*(1-S*(1-F))

	int_I = int(I)

	if   int_I == 0:
		R1 = V
		G1 = T
		B1 = P
	elif int_I == 1:
		R1 = Q
		G1 = V
		B1 = P
	elif int_I == 2:
		R1 = P
		G1 = V
		B1 = T
	elif int_I == 3:
		R1 = P
		G1 = Q
		B1 = V
	elif int_I == 4:
		R1 = T
		G1 = P
		B1 = V
	else           :
		R1 = V
		G1 = P
		B1 = Q

	R = int(R1 * 255)
	G = int(G1 * 255)
	B = int(B1 * 255)

	return Color(R,G,B)


def hsv_table_by_saturation(H, S1, S2, V, order):
    ctbl = []

    ds = (S2-S1)/order
    for i in range(order):
        S = S1 + ds*i
        ctbl.append(hsv(H, S, V))
    return ctbl

def create_color_table(H1, H2, S, V, order):
	cbtl = [(0,0,0)]*order
	dH, tempH=0,0

	if H1 > H2:
		H1, H2 = H2, H1

	dH = (H2 - H1)/order
	tempH = H1

	for i in range(order):
		cbtl[i] = hsv(tempH, S, V)
		tempH += dH;

	return cbtl