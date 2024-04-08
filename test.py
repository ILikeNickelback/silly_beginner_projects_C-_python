import os
import time
import math

def create_screen():
    screen_size = [50, 50]
    screen_fill = [['-'] * 50 for _ in range(50)]
    screen_center = [25, 25]
    return screen_size, screen_fill, screen_center

def print_shape(screen, coords, angle, center):
    for i in range(4):
        for coord in coords[i]:
            x, y = coord
            if 0 <= x < 50 and 0 <= y < 50:
                x, y = rotate_point(coord, center, angle)
                screen[x][y] = "X"
    return screen

def rotate_point(point, center, angle):
    angle_rad = math.radians(angle)
    x, y = point
    new_x = math.floor((x - center[0]) * math.cos(angle_rad) - (y - center[1]) * math.sin(angle_rad)) + center[0]
    new_y = math.floor((x - center[0]) * math.sin(angle_rad) + (y - center[1]) * math.cos(angle_rad)) + center[1]
    return new_x, new_y

def square_coord(center, size):
    top, bottom, left, right = [], [], [], []
    for i in range(size):
        top.append([center[0] - round(size/2), center[1] - round(size/2) + i])
        bottom.append([center[0] + round(size/2), center[1] - round(size/2) + i])
        left.append([center[0] - round(size/2) + i , center[1] - round(size/2)] )
        right.append([center[0] - round(size/2) + i  , center[1] + round(size/2)])
    square_coords = [top, bottom, left, right]

    return square_coords


if __name__ == '__main__':
    size, angle, size_change = 1, 1, 1
    while True:
        if size > 30:size_change = -1
        if size == 0:size_change = 1
        if angle > 360: angle = 0

        screen_size, screen_fill, screen_center = create_screen()
        square_coords = square_coord(screen_center, size)
        screen = print_shape(screen_fill, square_coords, angle, screen_center)

        for row in screen:print(' '.join(row))

        time.sleep(1/60)
        os.system('cls')
        angle += 1
        size += size_change

