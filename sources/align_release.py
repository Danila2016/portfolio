#!/usr/bin/env python

'''Cube alignment'''
class Vector:
    def __init__(self, x, y, z):
        self.coords = (x,y,z)
    def __add__(self, a):
        return Vector(self.x+a.x, self.y+a.y, self.z+a.z)
    def __sub__(self, a):
        return Vector(self.x-a.x, self.y-a.y, self.z-a.z)
    @property
    def x(self):
        return self.coords[0]
    @property
    def y(self):
        return self.coords[1]
    @property
    def z(self):
        return self.coords[2]
    def __repr__(self):
        return "({:0.4f}, {:0.4f}, {:0.4f})".format(*self.coords)

def multiply(c, a):
    return Vector(c*a.x, c*a.y, c*a.z)

def lincomb(a, b, c):
    return a + multiply(c, b - a)

def subtract_((a,b)):
    return a - b

def dot(a, b):
    return a.x*b.x + a.y*b.y + a.z*b.z

def cross(a, b):
    return Vector(a.y*b.z - a.z*b.y, -a.x*b.z + a.z*b.x, a.x*b.y - a.y*b.x)

def norm(a, base_norm2=1.0):
    b = Vector(a.x, a.y, a.z)
    c = 1.0
    for j in range(20):
        c *= 0.5 + 0.5*base_norm2/norm2(b)
        b = multiply(c, a)
    return 1.0/c

def norm2(a):
    return a.x*a.x + a.y*a.y + a.z*a.z

def v_norm2(a):
    return map(norm2, a)

def VectorF(x,y,z):
    return Vector(1.0*x,1.0*y,1.0*z)


def init_base():
    '''Initialize 3d points'''
    points = [VectorF(i-0.5,j-0.5,k-0.5) for i in range(2)
            for j in range(2)
            for k in range(2)]
    return points

def drag1(points, coef=0.1):
    '''Pull the lower and the upper points towards their positions'''
    dz =  VectorF(0, 0, 0.5)
    p = VectorF(-1, 0, 0)
    points[0] = lincomb(points[0], multiply(1.0/norm(p, 0.5), p) - dz, coef)
    p = VectorF(-1, 0, 0)
    points[1] = lincomb(points[1], multiply(1.0/norm(p, 0.5), p) + dz, coef)
    p = VectorF(1, 0, 0)
    points[-2] = lincomb(points[-2], multiply(1.0/norm(p, 0.5), p) - dz, coef)
    p = VectorF(1, 0, 0)
    points[-1] = lincomb(points[-1], multiply(1.0/norm(p, 0.5), p) + dz, coef)
    return points

def drag2(points, coef=0.1):
    '''Pull the lower and the upper points towards their final positions'''
    p = VectorF(0, 0, -1)
    points[0] = lincomb(points[0], multiply(1.0/norm(p, 0.75), p), coef)
    p = VectorF(0, 0, 1)
    points[-1] = lincomb(points[-1], multiply(1.0/norm(p, 0.75), p), coef)
    return points

def main_forces(points, max_force=0.01):
    '''Compute forces between points'''
    n = len(points)
    forces = [VectorF(0,0,0) for i in range(n)]
    for i, p in enumerate(points):
        for j, q in enumerate(points):
            if i != j:
                diff = p - q
                f = multiply(0.01/norm2(diff), diff)
                forces[i] += (f - multiply(dot(p, f)/norm2(p), p))

    while max(v_norm2(forces)) > max_force**2:
        for i, f in enumerate(forces):
            forces[i] = multiply(0.9, f)

    return forces

def normalise(points, max_shift=0.0001, T=1000, max_force=0.01, drag=False):
    '''Normalize points'''
    n = len(points)
    t = 0

    c = VectorF(0,0,0)
    for i, p in enumerate(points):
        c += p
    c = multiply(1.0/n, c)
    for i, p in enumerate(points):
        points[i] = p - c

    for t in range(T):
        i_iter = 1.0
        if drag:
            points = drag(points)

        while (i_iter == 1.0) or (max(v_norm2(map(subtract_, zip(points, old_points)))) > max_shift**2):
            old_points = points[:]

            forces = main_forces(points, max_force=max_force/i_iter)
            for i, f in enumerate(forces):
                points[i] += f
            i_iter += 1

            c = VectorF(0,0,0)
            for i, p in enumerate(points):
                c += p
            c = multiply(1.0/n, c)
            for i, p in enumerate(points):
                points[i] = p - c

            norms = [None]*n
            for i, p in enumerate(points):
                norms[i] = norm(p, 0.75)
            for i, p in enumerate(points):
                points[i] = multiply(1.0/norms[i], p) 

    return points

def compute_dists2(points):
    '''Distances between subsequent points'''
    dists = []
    for p, q in zip(points[:-1], points[1:]):
        dists.append(norm2(p - q))
    return dists
	

def init():
    points = init_base()
    print(points)
       
    points = normalise(points, drag=False)
    print(points)

    before = compute_dists2(points)

    points = normalise(points, drag=drag1)
    print(points)

    points = normalise(points, drag=drag2)
    print(points)

    after = compute_dists2(points)
    for p, q in zip(before, after):
        assert(abs(p-q) < 1e-4)
      
'''
[(-0.0000, 0.0000, -0.8660), (-0.8165, -0.0000, -0.2887), (0.4082, 0.7071, -0.2887), (-0.4082, 0.7071, 0.2887), (0.4082, -0.7071, -0.2887), (-0.4082, -0.7071, 0.2887), (0.8165, 0.0000, 0.2887), (0.0000, 0.0000, 0.8660)]
'''

init() 

