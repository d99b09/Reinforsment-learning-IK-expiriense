import math as m
import random as r


def coord_to_polar(x, y, z):
    ro = m.sqrt(x**2 + y**2 + z**2)
    c = x/m.sqrt(x**2 + y**2)
    s = y/m.sqrt(x**2 + y**2)

    teta = m.asin(z/ro)

    if s == 0:
        if c == 1:
            fi = 0
        else:
            fi = m.pi
    elif c == 0:
        if s == 1:
            fi = m.pi/2
        else:
            fi = 3 * m.pi/2
    elif s > 0:
        if c > 0:
            fi = m.acos(c)
        else:
            fi = m.pi - m.asin(s)
    else:
        if c < 0:
            fi = 2*m.pi - m.acos(c)
        else:
            fi = 2 * m.pi - m.acos(c)

    return ro, fi, teta

if __name__ == '__main__':
    ro = r.random()
    fi = r.uniform(0, 2*m.pi)
    teta = r.uniform(0, m.pi / 2)
    print(ro, fi, teta)
    x = ro * m.cos(teta) * m.cos(fi)
    y = ro * m.cos(teta) * m.sin(fi)
    z = ro * m.sin(teta)
    print(coord_to_polar(x, y, z))


