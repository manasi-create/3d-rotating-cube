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
scale = 14  # Increased scale for better fill

vertices = [
    (-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1),
    (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)
]

edges = [
    (0,1), (1,2), (2,3), (3,0), (4,5), (5,6),
    (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)
]

faces = [
    (0,1,2,3), (4,5,6,7), (0,3,7,4),
    (1,5,6,2), (0,4,5,1), (2,3,7,6)
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
    z_clamped = max(-3, min(z, 3))
    normalized_z = (z_clamped + 3) / 6  # 0 to 1 range
    return "!@#$:;=*.~,"[min(10, int(normalized_z * 11))]

def raster_quad(v1, v2, v3, v4, buffer, z_buffer):
    points = [v1, v2, v3, v4]
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    min_x = max(0, int(min(x_coords)))
    max_x = min(columns-1, int(max(x_coords)))
    min_y = max(0, int(min(y_coords)))
    max_y = min(rows-1, int(max(y_coords)))
    
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            inside = True
            for i in range(4):
                x0, y0, _ = points[i]
                x1, y1, _ = points[(i+1)%4]
                edge = (x1 - x0) * (y - y0) - (y1 - y0) * (x - x0)
                if edge < 0:
                    inside = False
                    break
            if inside:
                # Calculate depth as average of all four points
                z = sum(p[2] for p in points) / 4
                if z > z_buffer[y][x]:
                    z_buffer[y][x] = z
                    buffer[y][x] = get_char(z)

angle_x = angle_y = angle_z = 0

try:
    while True:
        buffer = [[' ']*columns for _ in range(rows)]
        z_buffer = [[-float('inf')]*columns for _ in range(rows)]
        rotated = [rotate_z(rotate_y(rotate_x(v, angle_x), angle_y), angle_z) for v in vertices]
        screen_points = [(project(v)[0], project(v)[1], v[2]) for v in rotated]

        # Fill faces with solid characters
        for face in faces:
            v1, v2, v3, v4 = [screen_points[i] for i in face]
            raster_quad(v1, v2, v3, v4, buffer, z_buffer)

        # Draw edges with same characters
        for edge in edges:
            i0, i1 = edge
            x0, y0, z0 = screen_points[i0]
            x1, y1, z1 = screen_points[i1]
            line = bresenham(x0, y0, x1, y1)
            if line:
                n = len(line)
                for idx, (x, y) in enumerate(line):
                    t = idx/(n-1) if n>1 else 0
                    current_z = z0 + t*(z1 - z0)
                    if 0 <= x < columns and 0 <= y < rows and current_z > z_buffer[y][x]:
                        z_buffer[y][x] = current_z
                        buffer[y][x] = get_char(current_z)

        os.system('cls' if os.name == 'nt' else 'clear')
        print('\n'.join(''.join(row) for row in buffer))
        
        angle_x += 0.08
        angle_y += 0.12
        angle_z += 0.04
        time.sleep(0.08)

except KeyboardInterrupt:
    pass
