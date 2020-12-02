import time
import multiprocessing
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

import pygame
import rx
from rx.operators import subscribe_on, observe_on
from rx.scheduler import ThreadPoolScheduler
from rx.scheduler.mainloop import PyGameScheduler

from tetris.model.game import (
    Block,
    PieceType,
    PieceOrientation,
    Piece,
    create_new_state,
)
from tetris.model.gameplay import MoveTimer

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

TURN_DURATION_SEC = 10

ui_scheduler = PyGameScheduler(pygame)
thread_pool_scheduler = ThreadPoolScheduler(multiprocessing.cpu_count())


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
    player: Any
    square_size: Any = SQUARE_SIZE
    square_border_width: Any = SQUARE_BORDER_WIDTH
    square_border_color: Any = SQUARE_BORDER_COLOR
    text_font_primary: Any = field(
        default_factory=lambda: pygame.font.SysFont(TEXT_FONT_FAMILY, 30, True, False))
    text_color: Any = TEXT_COLOR
    background_color: Any = BACKGROUND_COLOR
    get_color_for_piece_type: Any = lambda piece_type: COLOR_BY_PIECE_TYPE[piece_type]
    turn_duration_sec: Any = TURN_DURATION_SEC

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

    def draw_current_piece(self, piece_type):
        color = self.get_color_for_piece_type(piece_type)
        piece = Piece(piece_type, PieceOrientation.UP)
        for placement in piece.block_placements:
            self.draw_block(
                color,
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

    def update_display(self, board, piece_type, is_game_over, get_block_color):
        self.draw_background()

        self.draw_current_piece(piece_type)
        self.draw_board(board, get_block_color)

        if is_game_over:
            self.draw_game_over()

        pygame.display.flip()

    def subscribe_move(self, state, color_by_block, display_buffer):
        move = None
        piece = None
        color_by_block = {**color_by_block}

        def set_move(new_move):
            nonlocal move
            nonlocal piece
            
            if not move == new_move:
                move = new_move
                # this is for showing the move currently being considered
                if move:
                    # for now, very dumb way of doing opacity since the background is black
                    # TODO: make it less dumb
                    piece = state.get_piece_for_move(move)
                    piece_color = tuple(v / 8 for v in self.get_color_for_piece_type(state.piece_type))
                    new_color_by_block = {**color_by_block, **{p.val: piece_color for p in piece.block_placements}}
                    new_state = state.play_piece(piece, move.col)

                    display_buffer.append((new_state.board, state.piece_type, not move, lambda b: new_color_by_block[b]))

        def play_move():
            nonlocal color_by_block

            if move:
                piece_color = self.get_color_for_piece_type(piece.piece_type)
                new_color_by_block = {**color_by_block, **{p.val: piece_color for p in piece.block_placements}}
                new_state = state.play_piece(piece, move.col)
                self.subscribe_move(new_state, new_color_by_block, display_buffer)
                color_by_block = new_color_by_block
            else:
                new_state = state
                self.is_playing = False

            display_buffer.append((new_state.board, new_state.piece_type, not move, lambda b: color_by_block[b]))

        self.player.get_move_obs(state, MoveTimer(self.turn_duration_sec)).pipe(
            subscribe_on(thread_pool_scheduler),
            observe_on(ui_scheduler),
        ).subscribe(
            on_next=set_move,
            on_completed=play_move,
        )

    def play_game(self):
        pygame.display.set_caption("Tetris")

        self.is_playing = True
        display_buffer = []

        # TODO: pass around single mutable state object
        self.subscribe_move(create_new_state(self.board), {}, display_buffer)

        while True:
            ui_scheduler.run()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            if display_buffer:
                self.update_display(*display_buffer.pop(0))

            # time.sleep(0.1)
