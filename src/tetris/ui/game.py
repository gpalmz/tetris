import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

import pygame
from rx.scheduler.mainloop import PyGameScheduler
from rx.subject import Subject
from rx.operators import subscribe_on, observe_on

from common.util.concurrency import rx_background_scheduler
from tetris.model.game import PieceType, PieceOrientation, Piece

RGB_WHITE = (255, 255, 255)
RGB_BLACK = (0, 0, 0)

ROW_COUNT = 20
COL_COUNT = 10

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

pygame_scheduler = PyGameScheduler(pygame)


@contextmanager
def pygame_session():
    pygame.init()
    try:
        yield
    finally:
        pygame.quit()


@dataclass
class GameDisplayState:
    board: Any = None
    piece_type: Any = None
    score: Any = None
    is_game_over: Any = None
    get_block_color: Any = None


def if_present(optional, default):
    return optional if optional is not None else default


def update_display_state(state, update):
    return GameDisplayState(
        board=if_present(update.board, state.board),
        piece_type=if_present(update.piece_type, state.piece_type),
        score=if_present(update.score, state.score),
        is_game_over=if_present(update.is_game_over, state.is_game_over),
        get_block_color=if_present(update.get_block_color, state.get_block_color)
    )


def scale_opacity(color, opacity):
    return tuple(channel * opacity for channel in color)


@dataclass
class GameDisplay:
    conductor: Any
    row_count = ROW_COUNT
    col_count = COL_COUNT
    square_size: Any = SQUARE_SIZE
    square_border_width: Any = SQUARE_BORDER_WIDTH
    square_border_color: Any = SQUARE_BORDER_COLOR
    text_font_primary: Any = field(default_factory=lambda: pygame.font.SysFont(TEXT_FONT_FAMILY, 30, True, False))
    text_color: Any = TEXT_COLOR
    background_color: Any = BACKGROUND_COLOR
    get_color_for_piece_type: Any = lambda piece_type: COLOR_BY_PIECE_TYPE[piece_type]
    key_event_subject: Any = Subject()
    state: Any = GameDisplayState()
    display_buffer: Any = field(default_factory=lambda: [])
    display_update_delay: Any = 0.1  # TODO: dynamic refresh rate based on buffer size

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
        self.draw_square(self.square_border_color, x, y, self.square_border_width)

    def draw_current_piece(self, piece_type):
        color = self.get_color_for_piece_type(piece_type)
        piece = Piece(piece_type, PieceOrientation.UP)
        for placement in piece.block_placements:
            self.draw_block(
                color,
                (placement.col + (self.col_count - piece.col_count) // 2) * self.square_size,
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

    def draw_score(self, score):
        self.display.blit(self.text_font_primary.render(
            f"Score: {score}", True, self.text_color), (175, 10))

    def update_state(self, update):
        self.state = update_display_state(self.state, update)

    def update_display(self, update):
        self.update_state(update)

        self.draw_background()

        self.draw_current_piece(self.state.piece_type)
        self.draw_board(self.state.board, self.state.get_block_color)
        self.draw_score(self.state.score)
        if self.state.is_game_over:
            self.draw_game_over()

        pygame.display.flip()

    def queue_display_update(self, update):
        self.display_buffer.append(update)

    def update_display_next(self):
        if self.display_buffer:
            self.update_display(self.display_buffer.pop(0))

    def run(self):
        pygame.display.set_caption("Tetris")

        while True:
            pygame_scheduler.run()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    self.key_event_subject.on_next(event)

            self.update_display_next()

            time.sleep(self.display_update_delay)

    def run_game(self):
        color_by_block = {}
        piece = None

        def end_game():
            self.queue_display_update(GameDisplayState(is_game_over=True))
            
        def handle_unconfirmed_state(state, move):
            nonlocal piece

            piece = state.get_piece_for_move(move)
            piece_color = scale_opacity(self.get_color_for_piece_type(piece.piece_type), 1 / 8)
            new_color_by_block = {**color_by_block, **{p.val: piece_color for p in piece.block_placements}}

            self.queue_display_update(
                GameDisplayState(
                    board=state.play_move(move).board,
                    get_block_color=lambda b: new_color_by_block[b],
                    piece_type=state.piece_type,
                )
            )

        def handle_state(state):
            nonlocal color_by_block

            piece_color = self.get_color_for_piece_type(piece.piece_type)
            new_color_by_block = {**color_by_block, **{p.val: piece_color for p in piece.block_placements}}
            color_by_block = {**new_color_by_block}

            self.queue_display_update(
                GameDisplayState(
                    board=state.board, 
                    get_block_color=lambda b: new_color_by_block[b],
                    piece_type=state.piece_type, 
                    score=0, # TODO: keep track of score in conductor
                )
            )

        self.conductor.unconfirmed_state_subject.pipe(
            subscribe_on(rx_background_scheduler),
            observe_on(pygame_scheduler),
        ).subscribe(
            lambda state_move: handle_unconfirmed_state(*state_move),
        )

        self.conductor.state_subject.pipe(
            subscribe_on(rx_background_scheduler),
            observe_on(pygame_scheduler),
        ).subscribe(
            on_next=handle_state, 
            on_completed=end_game,
        )

        self.conductor.run_game()
        self.run()
