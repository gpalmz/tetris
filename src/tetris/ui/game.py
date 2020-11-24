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

from common.util.iter import safe_get
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

TURN_DURATION_SEC = 0.5
END_GAME_DURATION_SEC = 10

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

    def display_game(self, board, piece, is_game_over, get_block_color):
        print('rendering')
        self.draw_background()

        self.draw_current_piece(piece, get_block_color)
        self.draw_board(board, get_block_color)

        if is_game_over:
            self.draw_game_over()

        pygame.display.flip()

    # TODO: rename?
    def subscribe_turn(self, state, color_by_block):
        moves = []

        def add_move(move):
            moves.append(move)
            print('move added:', move)

        def play_final_move():
            print('move count:', len(moves))
            
            # assume most recent move is best
            # TODO: figure out if something is wrong here; get rid of safe_get if possible
            move = safe_get(moves, -1)

            piece = state.get_piece_for_move(move) if move else Piece(state.piece_type, PieceOrientation.UP)

            # store colors for all the blocks in the piece so we can use them later
            piece_color = self.get_color_for_piece_type(state.piece_type)
            color_by_block.update({p.val: piece_color for p in piece.block_placements})

            print('adding display state')
            self.game_display_states.append((state.board, piece, not move, lambda b: color_by_block[b]))

            # TODO: clean deleted blocks out of color_by_block
            if move:
                self.subscribe_turn(state.play_piece(piece, move.col), {**color_by_block})
            else:
                self.is_playing = False

        self.player.get_move_obs(state, MoveTimer(100)).pipe(
            subscribe_on(thread_pool_scheduler),
            observe_on(ui_scheduler),
        ).subscribe(
        # self.player.get_move_obs(state, MoveTimer(1000)).subscribe(
            on_next=add_move,
            on_completed=play_final_move,
        )

    def play_game(self):
        pygame.display.set_caption("Tetris")

        self.is_playing = True
        self.game_display_states = []

        self.subscribe_turn(create_new_state(self.board), {})

        while self.is_playing:
            # print('main loop')
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return

            while self.game_display_states:
                self.display_game(*self.game_display_states.pop())
                time.sleep(self.turn_duration_sec)

            ui_scheduler.run()
        
        if self.game_display_states:
            self.display_game(*self.game_display_states.pop())
        
        time.sleep(self.end_game_duration_sec)
