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


def get_color_for_type(piece_type):
    return PIECE_TYPE_COLORS[piece_type]


class GameBoard():

    # TODO: parameterize all the constants above, use a factory with defaults
    def __init__(self, board, square_size=SQUARE_SIZE):
        self.board = board
        self.square_size = square_size
        self.cols = board.col_count
        self.rows = board.row_count
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
        state = create_new_state(self.board)
        self.display.fill(BACKGROUND_COLOR)
        pygame.display.flip()

        while True:
            move = select_move(state)
            if move is None:
                font = pygame.font.SysFont('Comic Sans', 20, True, False)
                text = font.render("You lost!", True, RGB_BLACK)
                self.display.blit(text, [20, 200])
                pygame.display.flip()
                break

            piece = state.get_piece_for_move(move)
            state = state.play_piece(piece, move.col)
            block_color = get_color_for_type(piece.piece_type)

            self.display.fill(BACKGROUND_COLOR)

            for placement in piece.block_placements:
                row = (placement.row + 1)
                col = placement.col + self.cols // 2 - piece.col_count // 2
                self.block_colors[placement.val] = block_color
                self.draw_square(block_color, col, row)
                self.draw_square(SQUARE_BORDER_COLOR, col, row, True)
                pygame.display.flip()

            for placement in state.board.block_placements:
                row = (placement.row + self.offset)
                cur_color = self.block_colors[placement.val]
                self.draw_square(cur_color, placement.col, row)
                self.draw_square(SQUARE_BORDER_COLOR, placement.col, row, True)
                pygame.display.flip()

            time.sleep(0.5)

        time.sleep(10)
        pygame.quit()
