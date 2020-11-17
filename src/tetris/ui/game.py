import pygame
import time
from tetris.model.game import PieceType, create_new_state
from tetris.model.mcts import select_move

SQUARE_SIZE = 20
SQUARE_BORDER_WIDTH = 2

RGB_WHITE = (255, 255, 255)
RGB_BLACK = (0, 0, 0)

BACKGROUND_COLOR = RGB_WHITE
PIECE_TYPE_COLORS = {
    PieceType.O: (94, 167, 143),
    PieceType.T: (127, 183, 129),
    PieceType.S: (177, 175, 209),
    PieceType.Z: (232, 234, 144),
    PieceType.J: (234, 200, 144),
    PieceType.L: (234, 155, 144),
    PieceType.I: (164, 238, 206),
}
SQUARE_BORDER_COLOR = RGB_BLACK
TEXT_COLOR = RGB_BLACK


def get_color_for_type(piece_type):
    return PIECE_TYPE_COLORS[piece_type]


class GameBoard():

    # TODO: parameterize all the constants above, use a factory with defaults
    def __init__(self, state, square_size=SQUARE_SIZE):
        self.state = state
        self.square_size = square_size
        self.cols = self.state.board.col_count
        self.rows = self.state.board.row_count
        self.offset = 5
        self.height = self.cols * self.square_size
        self.width = (self.rows + self.offset) * self.square_size
        self.block_colors = {}
        self.display = pygame.display.set_mode((self.height, self.width))

    def draw_square(self, color, x, y, has_border=False):
        pygame.draw.rect(
            self.display, 
            color, 
            [
                self.square_size * x, 
                self.square_size * y, 
                self.square_size, 
                self.square_size,
            ], 
            SQUARE_BORDER_WIDTH if has_border else 0,
        )

    def play_game(self):
        pygame.init()
        pygame.display.set_caption("Tetris")

        while True:
            self.display.fill(BACKGROUND_COLOR)

            move = select_move(self.state)
            if move is None:
                font = pygame.font.SysFont('Comic Sans', 20, True, False)
                text = font.render("You lost!", True, TEXT_COLOR)
                self.display.blit(text, [20, 200])
                pygame.display.flip()
                break

            piece = self.state.get_piece_for_move(move)
            piece_block_color = get_color_for_type(piece.piece_type)

            for placement in piece.block_placements:
                self.block_colors[placement.val] = piece_block_color

                row = (placement.row + 1)
                col = placement.col + self.cols // 2 - piece.col_count // 2
                self.draw_square(piece_block_color, col, row)
                self.draw_square(SQUARE_BORDER_COLOR, col, row, True)

            for placement in self.state.board.block_placements:
                row = (placement.row + self.offset)
                self.draw_square(self.block_colors[placement.val], placement.col, row)
                self.draw_square(SQUARE_BORDER_COLOR, placement.col, row, True)

            pygame.display.flip()

            self.state = self.state.play_piece(piece, move.col)

            time.sleep(0.5)

        time.sleep(10)
        pygame.quit()
