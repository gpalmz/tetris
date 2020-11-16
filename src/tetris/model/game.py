from enum import Enum, unique, auto
from dataclasses import dataclass
from random import randrange
from functools import cache

import numpy as np

import common.util.np as np_util


class Block:
    pass


def make_block():
    return Block()


def make_space():
    return 0


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
    LEFT = 3
    RIGHT = 1

    def rotated_90_cw(self, rotation_count=1):
        return PieceOrientation(self.value + rotation_count % 4)


@dataclass(frozen=True)
class GridPlacement:
    row: int
    col: int
    val: "any"  # TODO: type


def is_block(val):
    return isinstance(val, Block)


def get_block_placements_for_grid(grid):
    return [GridPlacement(coord[0], coord[1], val) for coord, val in np.ndenumerate(grid) if is_block(val)]


def get_block_grid_str(grid):
    return str(np.vectorize(lambda v: "X" if is_block(v) else " ")(grid))


@dataclass(frozen=True)
class Piece:
    piece_type: PieceType
    orientation: PieceOrientation

    @property
    @cache
    def grid(self):
        return np_util.arr_rotated_90_cw(
            get_grid_for_piece_type(self.piece_type),
            rotation_count=self.orientation.value,
        )

    @property
    @cache
    def block_placements(self):
        return get_block_placements_for_grid(self.grid)
        

    def __str__(self):
        return get_block_grid_str(self.grid)

    def rotated_90_cw(self, rotation_count=1):
        return Piece(
            self.piece_type,
            self.orientation.rotated_90_cw(rotation_count=rotation_count),
        )


@dataclass(frozen=True)
class Board:
    grid: np.array

    @property
    def row_count(self):
        return self.grid.shape[0]

    @property
    def col_count(self):
        return self.grid.shape[1]

    @property
    def block_placements(self):
        return get_block_placements_for_grid(self.grid)

    def __str__(self):
        return get_block_grid_str(self.grid)

    def is_coord_empty(self, row, col):
        """Determine whether a block can be placed at a given coordinate.

        If the coordinate is off the board, a block cannot be placed."""
        val = np_util.arr_get_safe(self.grid, (row, col))
        return not (is_block(val) or val is None)

    def place(self, placements):
        """Produce a new board similar to this one but with the specified coordinates filled."""
        new_grid = np.copy(self.grid)

        for placement in placements:
            new_grid[placement.row, placement.col] = placement.val

        return Board(new_grid)

    def is_row_full(self, row):
        return not any(self.is_coord_empty(row, col) for col in range(self.col_count))
    
    def clear_rows(self, rows):
        return Board(
            np.vstack(
                [
                    *[[make_space() for _ in range(self.col_count)] for _ in range(len(rows))],
                    *np.delete(self.grid, rows, axis=0)
                ]
            )
        )


def create_initial_board():
    return Board(np.zeros((20, 10), dtype=np.object))


@dataclass(frozen=True)
class Move:
    column: int
    orientation: PieceOrientation


def can_place_at_coord(board, piece, row, col):
    """Determine whether a piece can be placed in the given column.

    Return False if the piece overlaps another piece or is out of bounds."""
    for placement in piece.block_placements:
        if not board.is_coord_empty(placement.row + row, placement.col + col):
            return False
    return True


def get_placement_row(board, piece, col):
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

    @property
    def possible_moves(self):
        """Produce a list of all possible moves for the current state."""
        return [
            Move(col, orientation)
            for orientation in PieceOrientation
            for col in range(self.board.col_count)
            if can_place_at_coord(self.board, Piece(self.piece_type, orientation), 0, col)
        ]

    def play_move(self, move, should_clear_full_rows=True):
        """Produce a new state with the current piece placed and a new random piece type."""
        piece = Piece(self.piece_type, move.orientation)

        new_board = self.board.place(
            [
                GridPlacement(
                    placement.row + get_placement_row(self.board, piece, move.column), 
                    placement.col + move.column,
                    placement.val
                )
                for placement in piece.block_placements
            ]
        )

        if should_clear_full_rows:
            new_board = clear_full_rows(new_board)

        return piece, create_new_state(new_board)


def create_new_state(board):
    return State(board, PieceType(randrange(len(PieceType)) + 1))


def create_initial_state():
    return create_new_state(create_initial_board())
