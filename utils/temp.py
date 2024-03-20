import numpy as np
import matplotlib.pyplot as plt
import random

def linear_interpolation(p0, p1, t):
    """Linear interpolation function."""
    return (1 - t) * p0 + t * p1

def quadratic_bezier(p0, p1, p2, num_points=100):
    """Generate points on a quadratic Bézier curve."""
    t_values = np.linspace(0, 1, num_points)
    curve_points = []

    for t in t_values:
        p01 = linear_interpolation(p0, p1, t)
        p12 = linear_interpolation(p1, p2, t)
        curve_points.append(linear_interpolation(p01, p12, t))

    return np.array(curve_points)

# Define control points for the quadratic Bézier curve
p0 = np.array([0, 0])
p1 = np.array([abs(0 - 5)/random.random() + random.randrange(1, 2), abs(0 - 0)/random.random() + random.randrange(1, 2)])
p2 = np.array([5, 0])

# Generate points on the Bézier curve
curve_points = quadratic_bezier(p0, p1, p2)

# Plotting the Bézier curve and control points
plt.plot(curve_points[:, 0], curve_points[:, 1], label='Bézier Curve')
plt.scatter([p0[0], p1[0], p2[0]], [p0[1], p1[1], p2[1]], color='red', label='Control Points')
plt.title('Quadratic Bézier Curve with Linear Interpolation')
plt.legend()
plt.show()
