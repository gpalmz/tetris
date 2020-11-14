import pygame
import random
import time
from tetris.model.game import PieceType, State, create_new_state, generate_new_move

class GameBoard():

    def __init__(self, board, square_size=20):
        self.square_size = 20
        self.board = board
        self.cols = board.num_cols
        self.rows = board.num_rows
        self.height = self.cols * self.square_size
        self.width = self.rows * self.square_size

    def play_game(self):
        pygame.init()
        display = pygame.display.set_mode((self.height, self.width))
        pygame.display.set_caption("Tetris")
        died = False
        state = create_new_state(self.board)
        display.fill((220,220,220))
        pygame.display.flip()

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

            for i in range(self.rows):
                for j in range(self.cols):
                    is_colored = state.board.grid[i][j]

                    if is_colored:
                        pygame.draw.rect(display, (0,0,0), [self.square_size * j, self.square_size * i, self.square_size, self.square_size], 3)
                        pygame.draw.rect(display, (255,102,103), [self.square_size * j, self.square_size * i, self.square_size, self.square_size])
                        pygame.display.flip()

            time.sleep(1)

        time.sleep(10)
        pygame.quit()





