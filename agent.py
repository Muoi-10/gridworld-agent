WIDTH = 4
HEIGHT = 3
WALLS = [(1, 1)]


"""
width: int
height: int
walls: list of (a, b), index from 0

Return a 2d list of possible squares"""


def create_map(width, height, walls):
    map = [[0 for _ in range(width)] for _ in range(height)]
    for wall in walls:
        map[wall[0]][wall[1]] = 1
    return map


def main():
    map = create_map(WIDTH, HEIGHT, WALLS)
    print(map)


if __name__ == "__main__":
    main()
