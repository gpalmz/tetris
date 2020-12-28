import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import cached_property
from typing import Any

import pygame
from rx.scheduler.mainloop import PyGameScheduler
from rx.disposable import CompositeDisposable
from rx.subject import Subject
from rx import operators as op

from tetris.model.board import PieceType, PieceOrientation, Piece

RGB_WHITE = (255, 255, 255)
RGB_BLACK = (0, 0, 0)

DISPLAY_CAPTION = "Tetris"

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
    turn_time_remaining: Any = None
    get_block_color: Any = None


def if_present(opt, default):
    return opt if opt is not None else default


def update_display_state(state, update):
    return GameDisplayState(
        board=if_present(update.board, state.board),
        piece_type=if_present(update.piece_type, state.piece_type),
        score=if_present(update.score, state.score),
        is_game_over=if_present(update.is_game_over, state.is_game_over),
        turn_time_remaining=if_present(update.turn_time_remaining, state.turn_time_remaining),
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
    display_caption: Any = DISPLAY_CAPTION
    display_update_delay: Any = 0.1

    @property
    def header_height(self):
        return 4 * self.square_size

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
                (placement.col + 2 + (self.col_count - piece.col_count) // 2) * self.square_size,
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
            "Game over!", True, self.text_color), (10, 70))

    def draw_score(self, score):
        self.display.blit(self.text_font_primary.render(
            f"Score: {score}", True, self.text_color), (10, 40))

    def draw_turn_time_remaining(self, turn_time_remaining):
        self.display.blit(self.text_font_primary.render(
            f"Time: {turn_time_remaining}", True, self.text_color), (10, 10))

    def queue_display_update(self, update):
        self.state = update_display_state(self.state, update)

    def update_display(self):
        s = self.state

        self.draw_background()

        if s.piece_type is not None:
            self.draw_current_piece(s.piece_type)
        if s.board is not None and s.get_block_color is not None:
            self.draw_board(s.board, s.get_block_color)
        if s.score is not None:
            self.draw_score(s.score)
        if s.turn_time_remaining is not None:
            self.draw_turn_time_remaining(s.turn_time_remaining)
        if s.is_game_over:
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        pygame.display.set_caption(self.display_caption)

        while True:
            pygame_scheduler.run()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    self.key_event_subject.on_next(event)

            self.update_display()

            time.sleep(self.display_update_delay)

    def run_game(self):
        color_by_block = {}

        def end_game():
            game_disposable.dispose()

            self.queue_display_update(GameDisplayState(is_game_over=True))
            
        def handle_move(game_state, move, is_move_final):
            nonlocal color_by_block

            if game_state is None:
                return

            piece = game_state.get_piece_for_move(move)
            piece_color = self.get_color_for_piece_type(piece.piece_type)

            if not is_move_final:
                piece_color = scale_opacity(piece_color, 1 / 8)

            new_game_state = game_state.play_move(move)
            new_color_by_block = {**{p.val: piece_color for p in piece.block_placements}, **color_by_block}

            if is_move_final:
                # throw out blocks that have been cleared
                new_game_state_blocks = set(p.val for p in new_game_state.board.block_placements)
                color_by_block = {
                    b: c for b, c in new_color_by_block.items() if b in new_game_state_blocks
                }

            self.queue_display_update(
                GameDisplayState(
                    board=new_game_state.board,
                    get_block_color=lambda b: new_color_by_block[b],
                    piece_type=game_state.piece_type,
                    score=new_game_state.score if is_move_final else None,
                )
            )

        game_disposable = CompositeDisposable(
            self.conductor.move_subject.subscribe(
                on_next=lambda v: handle_move(*v) if v is not None else None, 
                on_completed=end_game,
                scheduler=pygame_scheduler,
            ),
            self.conductor.turn_time_remaining_subject.subscribe(
                lambda t: self.queue_display_update(GameDisplayState(turn_time_remaining=t)),
                scheduler=pygame_scheduler,
            ),
        )

        self.conductor.run_game()
        self.run()
