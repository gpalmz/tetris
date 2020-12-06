from enum import Enum, unique, auto
from dataclasses import dataclass
from random import randrange
from functools import cached_property
from collections import namedtuple

import numpy as np

import common.util.np as np_util


class Block:
    __slots__ = []


def make_block():
    return Block()


def make_space():
    return 0


def is_block(val):
    return isinstance(val, Block)


@unique
class PieceType(Enum):
    I = auto()
    O = auto()
    T = auto()
    S = auto()
    Z = auto()
    J = auto()
    L = auto()


def get_grid_for_piece_type(piece_type):
    b = make_block
    s = make_space

    if piece_type == PieceType.I:
        grid = [
            [b(), b(), b(), b()],
        ]
    elif piece_type == PieceType.O:
        grid = [
            [b(), b()],
            [b(), b()],
        ]
    elif piece_type == PieceType.T:
        grid = [
            [b(), b(), b()],
            [s(), b(), s()],
        ]
    elif piece_type == PieceType.S:
        grid = [
            [s(), b(), b()],
            [b(), b(), s()],
        ]
    elif piece_type == PieceType.Z:
        grid = [
            [b(), b(), s()],
            [s(), b(), b()],
        ]
    elif piece_type == PieceType.J:
        grid = [
            [b(), s(), s()],
            [b(), b(), b()],
        ]
    elif piece_type == PieceType.L:
        grid = [
            [s(), s(), b()],
            [b(), b(), b()],
        ]

    return np.array(grid)


@unique
class PieceOrientation(Enum):
    UP = 0
    DOWN = 2
    LEFT = 1
    RIGHT = 3

    def rotated_90_ccw(self, rotation_count=1):
        return PieceOrientation(self.value + rotation_count % 4)


GridPlacement = namedtuple("GridPlacement", "row col val")


def get_block_placements_for_grid(grid):
    return [GridPlacement(coord[0], coord[1], val) for coord, val in np.ndenumerate(grid) if is_block(val)]


def get_block_grid_str(grid):
    return str(np.vectorize(lambda v: "X" if is_block(v) else " ")(grid))


@dataclass(frozen=True)
class Piece:
    piece_type: PieceType
    orientation: PieceOrientation

    @cached_property
    def grid(self):
        return np.rot90(get_grid_for_piece_type(self.piece_type), k=self.orientation.value)

    @cached_property
    def row_count(self):
        return self.grid.shape[0]

    @cached_property
    def col_count(self):
        return self.grid.shape[1]

    @cached_property
    def block_placements(self):
        return get_block_placements_for_grid(self.grid)

    def __str__(self):
        return get_block_grid_str(self.grid)

    def rotated_90_ccw(self, rotation_count=1):
        return Piece(
            self.piece_type,
            self.orientation.rotated_90_ccw(rotation_count=rotation_count),
        )


# NOTE: to see the absolute worst bug in the world, remove "eq=False" and use
# the functools.cache annotation on any method
@dataclass(frozen=True, eq=False)
class Board:
    grid: np.array

    @cached_property
    def row_count(self):
        return self.grid.shape[0]

    @cached_property
    def col_count(self):
        return self.grid.shape[1]

    @cached_property
    def block_placements(self):
        return get_block_placements_for_grid(self.grid)

    def __str__(self):
        return get_block_grid_str(self.grid)

    def is_coord_empty(self, row, col):
        """Determine whether a block can be placed at a given coordinate.

        If the coordinate is off the board, a block cannot be placed."""
        val = np_util.arr_get_safe(self.grid, (row, col))
        return not (is_block(val) or val is None)

    def is_row_full(self, row):
        return not any(self.is_coord_empty(row, col) for col in range(self.col_count))

    def place(self, placements):
        """Produce a new board similar to this one but with the specified coordinates filled."""
        new_grid = np.copy(self.grid)

        for placement in placements:
            new_grid[placement.row, placement.col] = placement.val

        return Board(new_grid)

    def clear_rows(self, rows):
        return Board(
            np.vstack(
                [
                    *[[make_space() for _ in range(self.col_count)]
                      for _ in range(len(rows))],
                    *np.delete(self.grid, rows, axis=0)
                ]
            )
        )


def create_initial_board():
    grid = np.zeros((20, 10), dtype=np.object)
    grid.flags.writeable = False
    return Board(grid)


Move = namedtuple("Move", "col orientation")


def can_place_at_coord(board, piece, row, col):
    """Determine whether a piece can be placed in the given column.

    Return False if the piece overlaps another piece or is out of bounds."""
    for placement in piece.block_placements:
        if not board.is_coord_empty(placement.row + row, placement.col + col):
            return False
    return True


def get_lowest_row(board, piece, col):
    """Determine the bottommost row in which a piece can be placed given a column.

    Pieces are automatically placed as far down as possible. Determine the row here."""
    placement_row = 0
    for row in range(board.row_count):
        if not can_place_at_coord(board, piece, row, col):
            # Break loop since the piece can't pass through existing blocks.
            break
        placement_row = row
    return placement_row


def clear_full_rows(board):
    return board.clear_rows(tuple(row for row in range(board.row_count) if board.is_row_full(row)))


@dataclass(frozen=True)
class State:
    board: Board
    piece_type: PieceType

    @cached_property
    def possible_moves(self):
        """Produce a list of all possible moves for the current state."""
        return [
            Move(col, orientation)
            for orientation in PieceOrientation
            for col in range(self.board.col_count)
            if can_place_at_coord(self.board, Piece(self.piece_type, orientation), 0, col)
        ]

    def get_piece_for_move(self, move):
        return Piece(self.piece_type, move.orientation)

    def play_piece(self, piece, col):
        return create_new_state(
            clear_full_rows(
                self.board.place(
                    tuple(
                        GridPlacement(
                            p.row + get_lowest_row(self.board, piece, col),
                            p.col + col,
                            p.val,
                        )
                        for p in piece.block_placements
                    )
                )
            )
        )

    def play_move(self, move):
        """Produce a new state with the current piece placed and a new random piece type."""
        return self.play_piece(self.get_piece_for_move(move), move.col)


def create_new_state(board):
    return State(board, PieceType(randrange(len(PieceType)) + 1))


def create_initial_state():
    return create_new_state(create_initial_board())
