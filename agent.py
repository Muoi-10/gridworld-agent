import random

WIDTH = 4
HEIGHT = 3
WALLS = [[0, 1]]
RATE = 0.8
INITIAL_STATE = [0, 0]


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


def get_reward(state, grid):
    """Return reward of a state: R(S)"""
    if is_wall(grid, state):
        return None
    if state == [0, 3]:
        return 1
    if state == [1, 3]:
        return -1
    return -0.04


def policy_iteration(grid):
    """Train an agent by policy iteration
    Return policy pi"""
    ...


def value_iteration(grid):
    """Train an agent using value iteration
    Return policy pi"""
    ...


class Agent:
    def __init__(self, training_method):
        self.training_method = training_method
        self.policy = [[None for _ in range(WIDTH)] for _ in range(HEIGHT)]

    def train(self, grid):
        if self.training_method == "value":
            # Perform value iteration
            ...
        elif self.training_method == "policy":
            # Perform policy iteration
            ...

    def pick(self, state, grid):
        """Return the optimal step from a state."""
        ...

    def play(self, state, grid):
        """Take actions from state until the end.
        Return the sequence from state to the end state"""


def main():
    grid = create_grid(WIDTH, HEIGHT, WALLS)
    agent_1 = Agent("value")
    agent_2 = Agent("policy")
    agent_1.train(grid)
    agent_2.train(grid)
    agent_1.play(INITIAL_STATE, grid)
    agent_2.play(INITIAL_STATE, grid)


if __name__ == "__main__":
    main()
