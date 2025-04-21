import pygame
import math
from pygame.locals import *

angle1 = 45  # -
angle2 = 30  # |
distance = 10

light_position = (0,0,10)
alpha = 2.0
beta = 1.0
u_res = 50 # количество точек вдоль ленты (условно горизонталь)
v_res = 10 # количество точек по толщине ленты ( условно вертикаль)

def f_points(alpha, beta, u_res, v_res):
    points = []
    for i in range(u_res):
        u = 2 * math.pi * i / (u_res - 1)  # чтобы u менялось от 0 до 2pi на одинаковую величину
        for j in range(v_res):
            v = -0.5 + j / (v_res - 1)   # чтобы v менялось от -0.5 до 0.5

            x = (alpha + v * math.cos(u / 2)) * math.cos(u)
            y = (alpha + v * math.cos(u / 2)) * math.sin(u)
            z = beta * v * math.sin(u / 2)

            points.append((x, y, z))
    return points


def normal(p1, p2, p3):
    u = (p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2])  # вектор p1p2
    v = (p3[0] - p1[0], p3[1] - p1[1], p3[2] - p1[2])  # вектор p1p3
    x = u[1] * v[2] - u[2] * v[1]
    y = u[2] * v[0] - u[0] * v[2]
    z = u[0] * v[1] - u[1] * v[0]
    length = math.sqrt(x**2 + y**2 + z**2)
    return (x/length, y/length, z/length)
def intens(normal, light):
    intensiv = normal[0] * light[0] + normal[1] * light[1] + normal[2] * light[2]
    return max(0.0, min(1.0, intensiv))

light_dir = (light_position[0], light_position[1], light_position[2])
length = math.sqrt(light_dir[0]**2 + light_dir[1]**2 + light_dir[2]**2)
light_dir = (light_dir[0]/length, light_dir[1]/length, light_dir[2]/length)


def draw_f(screen, points, u_res, v_res, width, height, angle1, angle2, distance):
    for i in range(u_res - 1):
        for j in range(v_res - 1):
            p1 = points[i * v_res + j]
            p2 = points[(i + 1) * v_res + j]
            p3 = points[(i + 1) * v_res + (j + 1)]
            p4 = points[i * v_res + (j + 1)]

            p1_2d = make_3d_to_2d(*p1, width, height, angle1, angle2, distance)
            p2_2d = make_3d_to_2d(*p2, width, height, angle1, angle2, distance)
            p3_2d = make_3d_to_2d(*p3, width, height, angle1, angle2, distance)
            p4_2d = make_3d_to_2d(*p4, width, height, angle1, angle2, distance)


            normal1 = normal(p1, p2, p3)
            normal2 = normal(p1, p3, p4)

            bright1 = intens(normal1, light_dir)
            bright2 = intens(normal2, light_dir)

            base_color = (0, 255, 0)
            color1 = (int(bright1 * base_color[0]), int(bright1 * base_color[1]), int(bright1 * base_color[2]))
            color2 = (int(bright2 * base_color[0]), int(bright2 * base_color[1]), int(bright2 * base_color[2]))

            draw_triangle(screen, color1, [p1_2d, p2_2d, p3_2d], (100, 100, 100), 1)
            draw_triangle(screen, color2, [p1_2d, p3_2d, p4_2d], (100, 100, 100), 1)


def make_3d_to_2d(x, y, z, width, height, angle1, angle2, distance):
    ay = math.radians(angle1)
    ax = math.radians(angle2)
    # поворот вокруг оси y
    x_rot = x * math.cos(ay) + z * math.sin(ay)
    z_rot = -x * math.sin(ay) + z * math.cos(ay)
    # поворот вокруг оси х
    y_rot = y * math.cos(ax) - z_rot * math.sin(ax)
    z_final = y * math.sin(ax) + z_rot * math.cos(ax)
    #
    koef = distance / (distance - z_final)
    x2d = width // 2 + x_rot * koef * 100
    y2d = height // 2 - y_rot * koef * 100
    return x2d, y2d

def draw_triangle(surface, color, points, border_color=None, border_width=0):
    min_x = max(0, min(p[0] for p in points))
    max_x = min(surface.get_width() - 1, max(p[0] for p in points))
    min_y = max(0, min(p[1] for p in points))
    max_y = min(surface.get_height() - 1, max(p[1] for p in points))

    def point_in_triangle(px, py):
        x1, y1 = points[0]
        x2, y2 = points[1]
        x3, y3 = points[2]

        d1 = (px - x2) * (y1 - y2) - (x1 - x2) * (py - y2)
        d2 = (px - x3) * (y2 - y3) - (x2 - x3) * (py - y3)
        d3 = (px - x1) * (y3 - y1) - (x3 - x1) * (py - y1)

        has_neg = (d1 < 0) or (d2 < 0) or (d3 < 0)
        has_pos = (d1 > 0) or (d2 > 0) or (d3 > 0)

        return not (has_neg and has_pos)

    for y in range(int(min_y), int(max_y) + 1):
        for x in range(int(min_x), int(max_x) + 1):
            if point_in_triangle(x, y):
                surface.set_at((x, y), color)
    pygame.draw.line(surface, border_color, points[0], points[1], border_width)
    pygame.draw.line(surface, border_color, points[1], points[2], border_width)
    pygame.draw.line(surface, border_color, points[2], points[0], border_width)




pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

font = pygame.font.SysFont('Arial', 15)
points = f_points(alpha, beta, u_res, v_res)

mouse = False
last_mouse = (0,0)
rotating = False

running = True
while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                rotating = not rotating
            elif event.key == K_UP:
                alpha = min(3.0, alpha + 0.2)
                points = f_points(alpha, beta, u_res, v_res)
            elif event.key == K_DOWN:
                alpha = max(1.0, alpha - 0.2)
                points = f_points(alpha, beta, u_res, v_res)
            elif event.key == K_RIGHT:
                beta = min(2.0, beta + 0.1)
                points = f_points(alpha, beta, u_res, v_res)
            elif event.key == K_LEFT:
                beta = max(0.5, beta - 0.1)
                points = f_points(alpha, beta, u_res, v_res)
        elif event.type == MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse = True
                rotating = False
                last_mouse = event.pos
        elif event.type == MOUSEBUTTONUP:
            if event.button == 1:
                mouse = False
        elif event.type == MOUSEMOTION:
            if mouse:
                temp_pos = event.pos
                dx = temp_pos[0] - last_mouse[0]
                dy = temp_pos[1] - last_mouse[1]
                angle1 += dx
                angle2 += dy
                last_mouse = temp_pos
                points = f_points(alpha, beta, u_res, v_res)
    if rotating:
        angle1 += 0.3
        angle2 += 0.3
        points = f_points(alpha, beta, u_res, v_res)

    screen.fill((255,255,255))
    draw_f(screen, points, u_res, v_res, width, height, angle1, angle2, distance)

    params_text = f"a: {alpha:.1f} (UP/DOWN)      b: {beta:.1f} (LEFT/RIGHT)"
    text_surface = font.render(params_text, True, (0,0,0))
    screen.blit(text_surface, (10, 10))

    pygame.display.flip()
    clock.tick(100)

pygame.quit()