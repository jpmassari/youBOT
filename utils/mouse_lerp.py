import noise
import argparse
import numpy as np
import matplotlib.pyplot as plt
import random
import ctypes

def __mouse_pos():
    user32 = ctypes.windll.user32
    point = ctypes.wintypes.POINT()
    user32.GetCursorPos(ctypes.byref(point))
    return point.x, point.y

def __linear_interpolation(p0, p1, t):
    return (1 - t) * p0 + t * p1

def __quadratic_bezier(p0, p1, p2, num_points=65000): #65000
    t_values = np.linspace(0, 1, num_points)
    curve_points = []
    for t in t_values:
        alpha_x = noise.pnoise1(5.46)
        alpha_y = noise.pnoise1(5.46)
        p01 = __linear_interpolation(p0, p1, t)
        p12 = __linear_interpolation(p1, p2, t)
        curve_points.append(__linear_interpolation(p01 + alpha_x, p12 + alpha_y, t))
    return np.array(curve_points)

def lerp(x, y):
    mouse_x, mouse_y = __mouse_pos()
    mouse_x = round(mouse_x)
    mouse_y = round(mouse_y)
    p0 = np.array([mouse_x, mouse_y])
    p1 = np.array([abs(mouse_x - x)/(random.random() + random.randrange(1, 2)), abs(mouse_y - y)/(random.random() + random.randrange(1, 2))])
    p2 = np.array([x, y])
    
    path = __quadratic_bezier(p0, p1, p2)
    
    #start + (goal - start) * alpha
    for x, y in path:
        ctypes.windll.user32.SetCursorPos(int(x), int(y))
    ctypes.windll.user32.SetCursorPos(int(x), int(y))

    """ plt.plot(path[:, 0], path[:, 1], label='Bézier Curve')
    plt.scatter([p0[0], p1[0], p2[0]], [p0[1], p1[1], p2[1]], color='red', label='Control Points')
    plt.title('Quadratic Bézier Curve with Linear Interpolation')
    plt.legend()
    plt.show() """

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Lerp the mouse cursor to a specified position.')
    parser.add_argument('--x', type=int, required=True, help='Target X coordinate')
    parser.add_argument('--y', type=int, required=True, help='Target Y coordinate')
    
    args = parser.parse_args()

    lerp(args.x, args.y)

    