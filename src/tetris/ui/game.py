import pygame
import time
from tetris.model.game import Block, PieceType, create_new_state
from tetris.model.strategy import select_move

SQUARE_SIZE = 30
SQUARE_BORDER_WIDTH = 2

RGB_WHITE = (255, 255, 255)
RGB_BLACK = (0, 0, 0)

BACKGROUND_COLOR = RGB_WHITE
COLOR_BY_PIECE_TYPE = {
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

TURN_DURATION_SEC = 0.5
END_GAME_DURATION_SEC = 10


def get_color_for_piece_type(piece_type):
    return COLOR_BY_PIECE_TYPE[piece_type]


class GameBoard():

    def __init__(self, board, square_size=SQUARE_SIZE):
        self.board = board
        self.square_size = square_size
        self.cols = self.board.col_count
        self.rows = self.board.row_count
        self.header_height = 5 * self.square_size
        self.width = self.cols * self.square_size
        self.height = self.rows * self.square_size + self.header_height
        self.display = pygame.display.set_mode((self.width, self.height))

    def draw_background(self):
        self.display.fill(BACKGROUND_COLOR)

    def draw_square(self, color, x, y, outline_width=0):
        pygame.draw.rect(
            self.display,
            color,
            [x, y, self.square_size, self.square_size],
            outline_width,
        )

    def draw_block(self, color, x, y):
        self.draw_square(color, x, y)
        self.draw_square(SQUARE_BORDER_COLOR, x, y, SQUARE_BORDER_WIDTH)

    def draw_current_piece(self, piece, get_block_color):
        for placement in piece.block_placements:
            self.draw_block(
                get_block_color(placement.val),
                (placement.col + (self.cols - piece.col_count) // 2) *
                self.square_size,
                (placement.row + 1) * self.square_size,
            )

    def draw_board(self, board, get_block_color):
        for placement in board.block_placements:
            self.draw_block(
                get_block_color(placement.val),
                placement.col * self.square_size,
                placement.row * self.square_size + self.header_height,
            )

    def draw_game_over(self):
        font = pygame.font.SysFont('Comic Sans', 20, True, False)
        text = font.render("You lost!", True, TEXT_COLOR)
        self.display.blit(text, [20, 200])

    def play_game(self):
        pygame.init()
        pygame.display.set_caption("Tetris")

        state = create_new_state(self.board)
        color_by_block = {}

        while True:
            self.draw_background()

            move = select_move(state)

            if move is None:
                self.draw_game_over()
                break

            piece = state.get_piece_for_move(move)

            # store colors for all the blocks in the piece so we can use them later
            piece_color = get_color_for_piece_type(piece.piece_type)
            for placement in piece.block_placements:
                color_by_block[placement.val] = piece_color

            self.draw_current_piece(piece, lambda b: color_by_block[b])
            self.draw_board(state.board, lambda b: color_by_block[b])

            pygame.display.flip()

            # advance to the next state
            state = state.play_piece(piece, move.col)

            # clear out color entries for blocks that are gone
            current_state_blocks = set(
                p.val for p in state.board.block_placements)
            color_by_block = {
                b: c for b, c in color_by_block.items() if b in current_state_blocks}

            time.sleep(TURN_DURATION_SEC)

        pygame.display.flip()
        time.sleep(END_GAME_DURATION_SEC)
        pygame.quit()
