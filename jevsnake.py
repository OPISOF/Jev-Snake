import random

import matplotlib.pyplot as plt
import pygame

from typesafe_sdk import TypeSafeClient, Choice

BLOCK = 20
FPS = 40
COMPAS = ["UP", "RIGHT", "DOWN", "LEFT"]

screen_width, screen_height = 720, 480

game_count = 0

r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)

def reset(snake, direction, food, score, head_y, head_x, game_count):
    game_count += 1
    score = 0
    snake = [[100, 100], [100 + BLOCK, 100]]

    while True:
        food = [
            random.randint(0, screen_width // BLOCK - 1) * BLOCK,
            random.randint(0, screen_height // BLOCK - 1) * BLOCK,
        ]
        if food not in snake:
            break

    direction = "DOWN"
    head_x, head_y = snake[0]

    return snake, direction, food, score, head_y, head_x, game_count


def game_step(food, score, direction, head_x, head_y):


    if direction == "DOWN":
        head_y = head_y + BLOCK
    if direction == "UP":
        head_y = head_y - BLOCK
    if direction == "RIGHT":
        head_x = head_x + BLOCK
    if direction == "LEFT":
        head_x = head_x - BLOCK

    if (
        head_x >= screen_width
        or head_y >= screen_height
        or head_x < 0
        or head_y < 0
        or [head_x, head_y] in snake[1:]
    ):
        return True, food, score, direction, head_x, head_y

    snake.insert(0, [head_x, head_y])

    if snake[0] != food:
        snake.pop()
    else:
        score += 1
        while True:
            food = [
                random.randint(0, screen_width // BLOCK - 1) * BLOCK,
                random.randint(0, screen_height // BLOCK - 1) * BLOCK,
            ]
            if food not in snake:
                break

    return False, food, score, direction, head_x, head_y


def get_frame(snake, food):

    display.fill("white")

    for x_position, y_position in snake:
        pygame.draw.rect(
            display,
            (r, g, b),
            pygame.Rect(x_position, y_position, BLOCK, BLOCK),
            width=4,
        )

    pygame.draw.rect(display, (b, r, g), pygame.Rect(food[0], food[1], BLOCK, BLOCK))

    score_text = font.render(f"Score: {score}", True, "black")
    display.blit(score_text, (25, 25))

    pygame.display.flip()
    clock.tick(FPS)


def check_crash(x, y, snake):
    if x >= screen_width or y >= screen_height or x < 0 or y < 0:
        return 1
    if [x, y] in snake[:-1]:
        return 1
    return 0 

def get_ai_direction(agent_state, statememt):
    response = client.system_one(
            state=statement,
            questions={
                "final_move": Choice(
                    instructions="How snake should move to win?",
                    criteria={
                        "RIGHT": "Turn right",
                        "STRAIGHT": "Keep direction",
                        "LEFT": "Turn left",
                        },
                    ),
                },
            )
    final_move = response.answers["final_move"].choice
    if final_move == "STRAIGHT":
        final_move = [0, 1, 0]
    elif final_move == "LEFT":
        final_move = [1, 0, 0]
    else:
        final_move = [0, 0, 1]
    return final_move



def interpretation_direction(direction, head_direction):

    index = COMPAS.index(direction)

    if head_direction[1] == 1:
        return direction
    if head_direction[0] == 1:
        return COMPAS[index - 1]
    if head_direction[2] == 1:
        if index + 1 == 4:
            return COMPAS[0]
        else:
            return COMPAS[index + 1]


def get_snake_STATE(head_x, head_y, food, snake):

    if direction == "UP":
        danger_left = [head_x - BLOCK, head_y]
        danger_straight = [head_x, head_y - BLOCK]
        danger_right = [head_x - BLOCK, head_y]

    if direction == "DOWN":
        danger_left = [head_x + BLOCK, head_y]
        danger_straight = [head_x, head_y + BLOCK]
        danger_right = [head_x + BLOCK, head_y]

    if direction == "RIGHT":
        danger_left = [head_x, head_y - BLOCK]
        danger_straight = [head_x + BLOCK, head_y]
        danger_right = [head_x, head_y + BLOCK]

    if direction == "LEFT":
        danger_left = [head_x, head_y + BLOCK]
        danger_straight = [head_x - BLOCK, head_y]
        danger_right = [head_x, head_y - BLOCK]

    danger = []

    danger.append(check_crash(danger_left[0], danger_left[1], snake))
    danger.append(check_crash(danger_straight[0], danger_straight[1], snake))
    danger.append(check_crash(danger_right[0], danger_right[1], snake))

    general_state = []

    general_state.append(int(head_x > food[0]))
    general_state.append(int(head_x < food[0]))
    general_state.append(int(head_y > food[1]))
    general_state.append(int(head_y < food[1]))

    if direction == "RIGHT":
        general_state = [
            general_state[2],
            general_state[3],
            general_state[1],
            general_state[0],
        ]
    if direction == "DOWN":
        general_state = [
            general_state[1],
            general_state[0],
            general_state[3],
            general_state[2],
        ]
    if direction == "LEFT":
        general_state = [
            general_state[3],
            general_state[2],
            general_state[0],
            general_state[1],
        ]

    state = []
    state = danger + general_state

    return state

def get_statement(agent_state):
    obj = {
            "The danger on the left": agent_state[0],
            "The danger on stright": agent_state[1],
            "The danger on the right": agent_state[2],
            "The food is to the left": agent_state[3],
            "The food is to the right": agent_state[4],
            "The food is in front of you": agent_state[5],
            "The food is behind you": agent_state[6]
            }
    return obj


# ===================================

plt.ion()


def plot(mit_score_series, score_series):
    plt.clf()
    plt.plot(score_series, marker="", linestyle="-", color="b")
    plt.plot(mit_score_series, marker="", linestyle="-", color="r")
    plt.title("learning...")
    plt.xlabel("Game number")
    plt.ylabel("Score")
    plt.grid(False)
    plt.ylim(0, max(max(mit_score_series, default=0), max(score_series, default=0)) + 5)
    plt.draw()
    plt.pause(0.1)


# ===================================

pygame.init()

display = pygame.display.set_mode((screen_width, screen_height))
clock = pygame.time.Clock()
font = pygame.font.Font(None, 24)

client = TypeSafeClient()

score_series = []
mit_score_series = []

snake, direction, food, score, head_y, head_x, game_count = reset(
    [], "DOWN", [], 0, 0, 0, 0
)

pressed = True

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pressed = False

            if event.key == pygame.K_TAB:
                pressed = True

            if event.key == pygame.K_BACKSPACE:
                snake, direction, food, score, head_y, head_x, game_count = reset(
                    snake, direction, food, score, head_y, head_x, game_count
                )

    agent_state = get_snake_STATE(head_x, head_y, food, snake)
    statement = get_statement(agent_state)
    head_direction = get_ai_direction(agent_state, statement)

    direction = interpretation_direction(direction, head_direction)

    gameover, food, score, direction, head_x, head_y = game_step(
        food, score, direction, head_x, head_y
    )

    if pressed == True:
        get_frame(snake, food)

    if gameover:
        score_series.append(score)

        total = 0

        for i in score_series:
            total += i

        mit_score_series.append(total / len(score_series))

        if game_count % 50 == 0:
            plot(mit_score_series, score_series)


        snake, direction, food, score, head_y, head_x, game_count = reset(
            snake, direction, food, score, head_y, head_x, game_count
        )
