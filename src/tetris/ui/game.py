import pygame
import random
import time
from tetris.model.game import PieceType, State, create_new_state, is_block, get_grid_for_piece_type
from tetris.model.mcts import select_move

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
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
        self.offset = 5
        self.height = self.cols * self.square_size
        self.width = (self.rows + self.offset) * self.square_size
        self.block_colors = {}
        self.display = pygame.display.set_mode((self.height, self.width))

    def fill_offset(self):
        for i in range(4):
            for j in range(self.cols):
                pygame.draw.rect(self.display, WHITE, [
                    self.square_size * j, self.square_size * i, self.square_size, self.square_size])

    def draw_square(self, color, x, y, has_border=False):
        if has_border:
            pygame.draw.rect(self.display, color, [
                             self.square_size * x, self.square_size * y, self.square_size, self.square_size], 3)
        else:
            pygame.draw.rect(self.display, color, [
                             self.square_size * x, self.square_size * y, self.square_size, self.square_size])

    def play_game(self):
        pygame.init()
        pygame.display.set_caption("Tetris")
        died = False
        state = create_new_state(self.board)
        self.display.fill(WHITE)
        pygame.display.flip()

        while not died:

            move = select_move(state)
            if move is None:
                font = pygame.font.SysFont('Comic Sans', 20, True, False)
                text = font.render("You lost!", True, BLACK)
                self.display.blit(text, [20, 200])
                pygame.display.flip()
                died = True

            cur_piece_type = state.piece_type
            piece = state.get_piece_for_move(move)
            cur_grid = piece.grid
            state = state.play_piece(piece, move.col)
            placements = piece.block_placements
            piece_type = piece.piece_type
            block_color = get_color_for_type(piece_type)

            self.fill_offset()
            self.display.fill(WHITE)
            for space in range(len(cur_grid)):
                for i, j in zip(range((len(cur_grid[space]))), range(self.cols // 2 - 1, self.cols // 2 - 1 + len(cur_grid[space]))):
                    if is_block(cur_grid[space][i]):
                        self.draw_square(block_color, j, (space + 1))
                        self.draw_square(BLACK, j, (space + 1), True)
                        pygame.display.flip()

            for placement in placements:
                self.block_colors[placement.val] = block_color

            for placement in state.board.block_placements:
                if is_block(placement.val):
                    cur_color = self.block_colors[placement.val]
                    self.draw_square(cur_color, placement.col, (placement.row + self.offset))
                    self.draw_square(BLACK, placement.col, (placement.row + self.offset), True)
                    pygame.display.flip()

            time.sleep(0.5)

        time.sleep(10)
        pygame.quit()
