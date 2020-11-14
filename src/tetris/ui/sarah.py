import pygame
import random
import time
from src.tetris.model.game import PieceType, State, create_new_state, generate_new_move
from src.tetris.model.demo_game import state_0, board_0


square_size = 20
board = board_0
cols = board.num_cols
rows = board.num_rows
height = cols * square_size
width = rows * square_size

pygame.init()
display = pygame.display.set_mode((height, width))

pygame.display.set_caption("Tetris")
 
died = False

clock = pygame.time.Clock()
state = create_new_state(board)

while not died:

    new_piece_type = random.choice(list(PieceType))
    new_piece = state.piece_type


    move = generate_new_move(state)
    if move is None:
        font = pygame.font.SysFont('Comic Sans', 20, True, False)
        text = font.render("You lost!", True, (0,0,0))
        display.blit(text, [20, 200])
        pygame.display.flip()
        break


    state = state.play_move(move)

    cur_col = move.column
    orientation = move.orientation

    display.fill((220,220,220))

    pygame.display.flip()


    for i in range(rows):
        for j in range(cols):
            is_colored = state.board.grid[i][j]

            if is_colored:
                pygame.draw.rect(display, (0,0,0), [square_size * j, square_size * i, square_size, square_size], 3)
                pygame.draw.rect(display, (255,102,103), [square_size * j, square_size * i, square_size, square_size])
                pygame.display.flip()

    time.sleep(1)

time.sleep(10)





