import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

import pygame

from tetris.model.game import (
    Block,
    PieceType,
    PieceOrientation,
    Piece,
    create_new_state,
)
from tetris.model.strategy import select_move

RGB_WHITE = (255, 255, 255)
RGB_BLACK = (0, 0, 0)

SQUARE_SIZE = 30
SQUARE_BORDER_WIDTH = 2
SQUARE_BORDER_COLOR = RGB_BLACK

TEXT_FONT_FAMILY = "Comic Sans"
TEXT_COLOR = RGB_WHITE

BACKGROUND_COLOR = RGB_BLACK

COLOR_BY_PIECE_TYPE = {
    PieceType.O: (94, 167, 143),
    PieceType.T: (127, 183, 129),
    PieceType.S: (177, 175, 209),
    PieceType.Z: (232, 234, 144),
    PieceType.J: (234, 200, 144),
    PieceType.L: (234, 155, 144),
    PieceType.I: (164, 238, 206),
}

TURN_DURATION_SEC = 0.5
END_GAME_DURATION_SEC = 10


@contextmanager
def pygame_session():
    pygame.init()
    try:
        yield
    finally:
        pygame.quit()


@dataclass
class GameDisplay:
    board: Any
    square_size: Any = SQUARE_SIZE
    square_border_width: Any = SQUARE_BORDER_WIDTH
    square_border_color: Any = SQUARE_BORDER_COLOR
    text_font_primary: Any = field(
        default_factory=lambda: pygame.font.SysFont(TEXT_FONT_FAMILY, 30, True, False))
    text_color: Any = TEXT_COLOR
    background_color: Any = BACKGROUND_COLOR
    get_color_for_piece_type: Any = lambda piece_type: COLOR_BY_PIECE_TYPE[piece_type]
    turn_duration_sec: Any = TURN_DURATION_SEC
    end_game_duration_sec: Any = END_GAME_DURATION_SEC

    @property
    def row_count(self):
        return self.board.row_count

    @property
    def col_count(self):
        return self.board.col_count

    @property
    def header_height(self):
        return 5 * self.square_size

    @property
    def height(self):
        return self.row_count * self.square_size + self.header_height

    @property
    def width(self):
        return self.col_count * self.square_size

    @cached_property
    def display(self):
        return pygame.display.set_mode((self.width, self.height))

    def draw_background(self):
        self.display.fill(self.background_color)

    def draw_square(self, color, x, y, outline_width=0):
        pygame.draw.rect(
            self.display,
            color,
            [x, y, self.square_size, self.square_size],
            outline_width,
        )

    def draw_block(self, color, x, y):
        self.draw_square(color, x, y)
        self.draw_square(self.square_border_color, x,
                         y, self.square_border_width)

    def draw_current_piece(self, piece, get_block_color):
        for placement in piece.block_placements:
            self.draw_block(
                get_block_color(placement.val),
                (placement.col + (self.col_count - piece.col_count) // 2) *
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
        self.display.blit(self.text_font_primary.render(
            "You lost!", True, self.text_color), (10, 10))

    def display_game(self, board, move, piece, get_block_color):
        self.draw_background()

        self.draw_current_piece(piece, get_block_color)
        self.draw_board(board, get_block_color)

        if not move:
            self.draw_game_over()

        pygame.display.flip()

    def play_game(self):
        pygame.display.set_caption("Tetris")

        state = create_new_state(self.board)
        color_by_block = {}

        while True:
            move = select_move(state)

            piece = state.get_piece_for_move(move) if move else Piece(
                state.piece_type, PieceOrientation.UP)

            # store colors for all the blocks in the piece so we can use them later
            piece_color = self.get_color_for_piece_type(state.piece_type)
            for placement in piece.block_placements:
                color_by_block[placement.val] = piece_color

            self.display_game(state.board, move, piece,
                              lambda b: color_by_block[b])

            if not move:
                break

            state = state.play_piece(piece, move.col)

            # clear out color entries for blocks that are gone
            current_state_blocks = set(
                p.val for p in state.board.block_placements)
            color_by_block = {
                b: c for b, c in color_by_block.items() if b in current_state_blocks}

            time.sleep(self.turn_duration_sec)

        time.sleep(self.end_game_duration_sec)
