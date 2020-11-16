import pygame
import random
import time
from tetris.model.game import PieceType, State, create_new_state, is_block
from tetris.model.mcts import select_move



def get_color_for_type(piece_type):
    piece_type_colors = {
        PieceType.O: (94, 167, 143),
        PieceType.T: (127, 183, 129),
        PieceType.S: (177, 175, 209),
        PieceType.Z: (232, 234, 144),
        PieceType.J: (234, 200, 144),
        PieceType.L: (234, 155, 144),
        PieceType.I: (164, 238, 206),
    }
    return piece_type_colors[piece_type]

class GameBoard():

    def __init__(self, board, square_size=20):
        self.board = board
        self.square_size = 20
        self.cols = board.col_count
        self.rows = board.row_count
        self.height = self.cols * self.square_size
        self.width = self.rows * self.square_size
        self.block_colors = {}


    def play_game(self):
        pygame.init()
        display = pygame.display.set_mode((self.height, self.width))
        pygame.display.set_caption("Tetris")
        died = False
        state = create_new_state(self.board)
        display.fill((220, 220, 220))
        pygame.display.flip()

        while not died:

            move = select_move(state)
            if move is None:
                font = pygame.font.SysFont('Comic Sans', 20, True, False)
                text = font.render("You lost!", True, (0, 0, 0))
                display.blit(text, [20, 200])
                pygame.display.flip()
                break

            piece, state = state.play_move(move)
            placements = piece.block_placements
            piece_type = piece.piece_type
            block_color = get_color_for_type(piece_type)

            for placement in placements:
                self.block_colors[placement.val] = block_color

            for i in range(self.rows):
                for j in range(self.cols):
                    space = state.board.grid[i][j]

                    if is_block(space):
                        cur_color = self.block_colors[space]

                        pygame.draw.rect(display, (0, 0, 0), [
                                         self.square_size * j, self.square_size * i, self.square_size, self.square_size], 3)
                        pygame.draw.rect(display, cur_color, [
                                         self.square_size * j, self.square_size * i, self.square_size, self.square_size])
                    else:
                        pygame.draw.rect(display, (255, 255, 255), [
                                         self.square_size * j, self.square_size * i, self.square_size, self.square_size])
                    pygame.display.flip()

            time.sleep(1)

        time.sleep(10)
        pygame.quit()
