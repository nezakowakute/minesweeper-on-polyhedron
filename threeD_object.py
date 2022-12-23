import math
from copy import copy

#point・・・(座標1、座標2・・・),
#surface・・・((面を構成する座標の配列(左手で、親指を突き出した方向を面の外側として、点を指の巻く方向に並べる。ただし、最初の3点がなす角の大きさは180度未満であること), 〃, 〃･･･, 色もしくは画像のパス), ・・・)
def draw(objects, light_vec, point_of_view, view_vec, width, height, scale=1024):
    view_vec.change_len()
    light_vec.change_len()
    surfaces = []
    points = []
    try:
        view_vecxz = vec3(view_vec.x, 0, view_vec.z)
        view_vecxz.change_len()
    except ZeroDivisionError:
        view_vecxz = vec3(0, 0, 1)
    anglexz = math.acos(view_vecxz.z)*(1 if view_vecxz.x>=0 else -1)
    angley = math.acos(round(view_vecxz*view_vec, 8))*(-1 if view_vec.y>=0 else 1)
    for obj in objects:
        surfaces.extend([i+len(points) for i in sur]+[light_color(normal_vec(sur, obj.points), light_vec, obj.color[i])] for i,sur in enumerate(obj.surfaces))
        points.extend((point+obj.center-point_of_view).rotate(anglexz, vec3(0, -1, 0)).rotate(angley, vec3(1, 0, 0)) for point in obj.points)
    surfaces = list(filter(lambda surface:all(map(lambda i:points[i].z>=0, surface[:-1])), surfaces))
    surfaces.sort(key=lambda surface:sum(map(lambda i:points[i].z, surface[:-1]))/(len(surface)-1), reverse=True)
    return tuple(filter(lambda surface:any(map(lambda i:0<=i[0]<=width and 0<=i[1]<=height, surface)), map(lambda surface:[(points[i].x/points[i].z*scale+width/2, points[i].y/points[i].z*scale+height/2) for i in surface[:-1]]+[surface[-1]], surfaces)))
def light_color(vec, light_vec, color):
    angle = math.acos(round(vec*light_vec,8))/math.pi
    return tuple(map(lambda i:max(0, min(255, i*angle)), color))
def normal_vec(polygon, points):
    vec = (points[polygon[0]]-points[polygon[1]])/(points[polygon[2]]-points[polygon[1]])
    vec.change_len()
    return vec
class threeD:
    def __init__(self, points, surfaces):
        if type(points[0]) == vec3:
            self.points = points
        else:
            self.points = [vec3(*i) for i in points]#頂点を保存する。
        self.surfaces = tuple(map(lambda i:i[:-1],surfaces))#面を保存する。
        self.color = [i[-1] for i in surfaces]
        self.center = vec3(0, 0, 0)#中心の座標を保存する。
    def move(self, vec):#自分自身を移動する。
        self.center+=vec
        for point in self.points:
            point+=vec
    def multip(self, scalar):#自分自身を拡大する。magはmagnificationの略
        for point in self.points:
            point*=scalar
    def rotate(self, angle, shaft):#自分自身を回転させる
        shaft.change_len()
        for point in self.points:
            point.srotate(angle, shaft)
    def distance(self, point_of_view):#視点からのオブジェクトの距離を返す
        return abs(self.center-point_of_view)
class image_threeD(threeD):
    def __init__(self, pos, xvec, yvec, image):
        y_len = len(image[0])
        super().__init__([pos+xvec*(i//(y_len+1))+yvec.multip(i%(y_len+1)) for i in range((len(image)+1)*(y_len+1))],\
            [(i+i//y_len, i+i//y_len+y_len+1, i+i//y_len+2+y_len, i+i//y_len+1, image[i//y_len][i%y_len]) for i in range((y_len-1)*len(image))])
class vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        self.update_length()
    def __eq__(self,other):
        return self.x == other.x and self.y == other.y and self.z == other.z
    def __add__(self,other):
        return vec3(self.x+other.x,self.y+other.y,self.z+other.z)
    def __sub__(self,other):
        return vec3(self.x-other.x,self.y-other.y,self.z-other.z)
    def __mul__(self,other):
        if type(other) in (int,float):
            return vec3(self.x*other,self.y*other,self.z*other)
        else:
            return self.x*other.x+self.y*other.y+self.z*other.z
    def __rmul__(self,other):
        return vec3(self.x*other,self.y*other,self.z*other)
    def __imul__(self,other):
        self.x *= other
        self.y *= other
        self.z *= other
        return self
    def __truediv__(self,other):
        if type(other)in(int,float):
            return vec3(self.x/other,self.y/other,self.z/other)
        else:
            return vec3(self.y*other.z-self.z*other.y, self.z*other.x-self.x*other.z, self.x*other.y-self.y*other.x)
    def __itruediv__(self,other):
        self.x /= other
        self.y /= other
        self.z /= other
        return self
    def __iadd__(self,other):
        self.x += other.x
        self.y += other.y
        self.z += other.z
        self.update_length()
        return self
    def __isub__(self,other):
        self.x -= other.x
        self.y -= other.y
        self.z -= other.z
        self.update_length()
        return self
    def __abs__(self):
        return self.length
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"
    def __round__(self,n=0):
        return vec3(round(self.x,n),round(self.y,n),round(self.z,n))
    def tuple(self):
        return (self.x, self.y, self.z)
    def srotate(self, angle, shaft):#ベクトルを回転させる
        shaft.change_len()
        cos = math.cos(angle)
        sin = math.sin(angle)#sinとcosの値を代入
        self.x, self.y, self.z = (cos+shaft.x**2*(1-cos))*self.x+(shaft.x*shaft.y*(1-cos)-shaft.z*sin)*self.y+(shaft.x*shaft.z*(1-cos)+shaft.y*sin)*self.z,\
            (shaft.x*shaft.y*(1-cos)+shaft.z*sin)*self.x+(cos+shaft.y**2*(1-cos))*self.y+(shaft.y*shaft.z*(1-cos)-shaft.x*sin)*self.z,\
                (shaft.x*shaft.z*(1-cos)-shaft.y*sin)*self.x+(shaft.y*shaft.z*(1-cos)+shaft.x*sin)*self.y+(cos+shaft.z**2*(1-cos))*self.z
    def rotate(self, angle, shaft):
        _vec = copy(self)
        _vec.srotate(angle, shaft)
        return _vec
    def change_len(self, length=1):#ベクトルの長さを変える
        self *= length/self.length
        self.length = length
    def update_length(self):
        self.length = math.sqrt(self.x**2+self.y**2+self.z**2)
    def return_pos(self):
        return (self.x,self.y,self.z)
