import math
import time
import os

def bresenham(x0, y0, x1, y1):
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    points = []
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
    return points

columns, rows = 80, 24
scale = 10

vertices = [
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
]

edges = [
    (0,1), (1,2), (2,3), (3,0), (4,5), (5,6),
    (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)
]

def rotate_x(point, angle):
    x, y, z = point
    return (x, y * math.cos(angle) - z * math.sin(angle),
            y * math.sin(angle) + z * math.cos(angle))

def rotate_y(point, angle):
    x, y, z = point
    return (x * math.cos(angle) + z * math.sin(angle),
            y, -x * math.sin(angle) + z * math.cos(angle))

def rotate_z(point, angle):
    x, y, z = point
    return (x * math.cos(angle) - y * math.sin(angle),
            x * math.sin(angle) + y * math.cos(angle), z)

def project(point):
    x, y, z = point
    return (int(x * scale + columns/2), int(y * scale + rows/2))

def get_char(z):
    z_clamped = max(-2, min(z, 2))
    normalized_z = (z_clamped + 2) / 4
    return "@#$*"[min(3, int(normalized_z * 4))]

angle_x = angle_y = angle_z = 0

try:
    while True:
        buffer = [[' ']*columns for _ in range(rows)]
        z_buffer = [[-float('inf')]*columns for _ in range(rows)]
        rotated = [rotate_z(rotate_y(rotate_x(v, angle_x), angle_y), angle_z) for v in vertices]
        screen_points = [(project(v)[0], project(v)[1], v[2]) for v in rotated]

        for edge in edges:
            i0, i1 = edge
            x0, y0, z0 = screen_points[i0]
            x1, y1, z1 = screen_points[i1]
            line = bresenham(x0, y0, x1, y1)
            n = len(line)
            if n == 0:
                continue
            
            for idx, (x, y) in enumerate(line):
                t = idx/(n-1) if n>1 else 0
                current_z = z0 + t*(z1 - z0)
                if 0 <= x < columns and 0 <= y < rows and current_z > z_buffer[y][x]:
                    z_buffer[y][x] = current_z
                    buffer[y][x] = get_char(current_z)

        os.system('cls' if os.name == 'nt' else 'clear')
        print('\n'.join(''.join(row) for row in buffer))
        
        angle_x += 0.1
        angle_y += 0.1
        angle_z += 0.05
        time.sleep(0.1)

except KeyboardInterrupt:
    pass