import random

WIDTH = 4
HEIGHT = 3
WALLS = [[0, 1]]
RATE = 0.8


def create_grid(width, height, walls):
    """
    width: int
    height: int
    walls: list of (a, b), index from 0

    Return a 2d list of possible squares"""

    grid = [[0 for _ in range(width)] for _ in range(height)]
    for wall in walls:
        grid[wall[0]][wall[1]] = 1
    return grid


def is_wall(grid, state):
    row = state[0]
    column = state[1]
    height = len(grid)
    width = len(grid[0])
    if (
        row < 0
        or row >= height
        or column < 0
        or column >= width
        or grid[row][column] == 1
    ):
        return True
    return False


def take_action(grid, state, action, rate):
    """
    Take in the agent's state and next action.
    Go according to action with probability: rate
    Otherwise goes to perpendicular direction with probability: (1 - rate) / 2

    state: [a, b], index from 0
    action: [x, y]: move to perform
    Return the next state

    """

    i = random.random()
    if i < rate:
        # Perform according to action
        height = len(grid)
        width = len(grid[0])
        new_row = state[0] + action[0]
        new_column = state[1] + action[1]
        # if the next state is a wall
        if not is_wall(grid, (new_row, new_column)):
            return [new_row, new_column]
        return state

    elif i >= rate and i < (rate + 1) / 2:
        # Perform the perpendicular to one way
        if action[0] == 0:
            action[0] = 1
            action[1] = 0
        else:
            action[0] = 0
            action[1] = 1
        return take_action(grid, state, action, 1)

    else:
        # Perform the perpendicular action to another way
        if action[0] == 0:
            action[0] = -1
            action[1] = 0
        else:
            action[0] = 0
            action[1] = -1
        return take_action(grid, state, action, 1)


def get_reward(state, walls):
    """Return reward of a state: R(S)"""
    if state in walls:
        ...


def main():
    grid = create_grid(WIDTH, HEIGHT, WALLS)


if __name__ == "__main__":
    main()
