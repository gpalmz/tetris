import pygame
import random
from ..model.game import PieceType, State, create_new_state, generate_new_move
from ..model.demo_game import state_0, board_0


def set_screen_dimensions(board):
  cols = board.num_cols
  rows = board.num_rows
  pygame.display.set_mode((cols * 20, rows * 20))


board = board_0
set_screen_dimensions(board)
pygame.display.set_caption("Tetris")
 
died = False

clock = pygame.time.Clock()

while not died:

    new_piece_type = random.choice(list(PieceType))
    cur_state = create_new_state(board)
    new_piece = cur_state.piece_type

    move = generate_new_move

    




