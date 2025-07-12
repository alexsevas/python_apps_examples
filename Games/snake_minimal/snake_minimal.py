# conda activate allpy310
# Ретро-игра «Змейка» в терминале
# pip install windows-curses для Windows


import curses
import random

def main(stdscr):
    curses.curs_set(0)
    sh, sw = stdscr.getmaxyx()
    w = curses.newwin(sh, sw, 0, 0)
    w.keypad(1)
    w.timeout(100)

    snk_x = sw//4
    snk_y = sh//2
    snake = [[snk_y, snk_x],
             [snk_y, snk_x-1],
             [snk_y, snk_x-2]]

    food = [random.randint(1, sh-2), random.randint(1, sw-2)]
    w.addch(food[0], food[1], curses.ACS_PI)

    key = curses.KEY_RIGHT
    while True:
        next_key = w.getch()
        key = key if next_key == -1 else next_key

        head = snake[0][:]
        if key == curses.KEY_DOWN:
            head[0] += 1
        elif key == curses.KEY_UP:
            head[0] -= 1
        elif key == curses.KEY_LEFT:
            head[1] -= 1
        elif key == curses.KEY_RIGHT:
            head[1] += 1
        else:
            continue

        if head in snake or head[0] in [0, sh-1] or head[1] in [0, sw-1]:
            break

        snake.insert(0, head)

        if head == food:
            food = None
            while food is None:
                nf = [random.randint(1, sh-2), random.randint(1, sw-2)]
                food = nf if nf not in snake else None
            w.addch(food[0], food[1], curses.ACS_PI)
        else:
            tail = snake.pop()
            w.addch(tail[0], tail[1], ' ')

        w.addch(head[0], head[1], curses.ACS_CKBOARD)

curses.wrapper(main)
