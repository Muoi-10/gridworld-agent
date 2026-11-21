import random

WIDTH = 4
HEIGHT = 3
WALLS = [(1, 1)]
RATE = 0.8
GAMMA = 0.99
ACTIONS = [[0, 1], [0, -1], [1, 0], [-1, 0]]


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


# Should've represented states as integers from the start
def state_to_num(state):
    num = state[0] * WIDTH + state[1]
    return num


def num_to_state(num):
    state = [0, 0]
    state[0] = num // WIDTH
    state[1] = num % WIDTH
    return state


# Should've done this before take_action function because take_action can utilize this function
def prob(grid, state, action, rate):
    """Return the probability distribution of new states after performing action at state"""

    p = {i: 0 for i in range(WIDTH * HEIGHT)}
    p[state_to_num(state)] = 0
    new_row = state[0] + action[0]
    new_col = state[1] + action[1]
    new_state = [new_row, new_col]
    if not is_wall(grid, new_state):
        p[state_to_num(new_state)] = rate
    else:
        p[state_to_num(state)] += rate

    if action[0] == 0:
        new_row = state[0] + 1
        new_row_2 = state[0] - 1
        if not is_wall(grid, [new_row, state[1]]):
            p[state_to_num([new_row, state[1]])] = (1 - rate) / 2
        else:
            p[state_to_num(state)] += (1 - rate) / 2
        if not is_wall(grid, [new_row_2, state[1]]):
            p[state_to_num([new_row_2, state[1]])] = (1 - rate) / 2
        else:
            p[state_to_num(state)] += (1 - rate) / 2

    elif action[1] == 0:
        new_col = state[1] + 1
        new_col_2 = state[1] - 1
        if not is_wall(grid, [state[0], new_col]):
            p[state_to_num([state[0], new_col])] = (1 - rate) / 2
        else:
            p[state_to_num(state)] += (1 - rate) / 2
        if not is_wall(grid, [state[0], new_col_2]):
            p[state_to_num([state[0], new_col_2])] = (1 - rate) / 2
        else:
            p[state_to_num(state)] += (1 - rate) / 2

    return p


class Agent:
    def __init__(self, training_method):
        self.training_method = training_method
        self.policy = [None for _ in range(WIDTH * HEIGHT)]

    def train(self, grid):
        if self.training_method == "value":
            # Perform value iteration
            self.value = [0 for _ in range(WIDTH * HEIGHT)]
            for _ in range(1000):
                for s in range(WIDTH * HEIGHT):
                    if not is_wall(grid, num_to_state(s)):
                        self.value[s] = get_reward(num_to_state(s), grid) + GAMMA * max(
                            sum(
                                prob(grid, num_to_state(s), a, RATE)[s_2]
                                * self.value[s_2]
                                for s_2 in range(WIDTH * HEIGHT)
                            )
                            for a in ACTIONS
                        )
        elif self.training_method == "policy":
            # Perform policy iteration
            ...

    def pick(self, state, grid):
        """Return the optimal step from a state."""
        if self.training_method == "value":
            a_max = [0, 0]
            expect_max = -float("inf")
            for a in ACTIONS:
                expect = sum(
                    prob(grid, state, a, RATE)[s] * self.value[s]
                    for s in range(WIDTH * HEIGHT)
                )
                if expect > expect_max:
                    expect_max = expect
                    a_max = a
        return a_max

    def play(self, state, grid):
        """Take actions from state until the end.
        Return the sequence from state to the end state"""


def main():
    grid = create_grid(WIDTH, HEIGHT, WALLS)
    agent = Agent("value")
    agent.train(grid)
    print(agent.pick([0, 0], grid))


if __name__ == "__main__":
    main()
