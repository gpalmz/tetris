from dataclasses import dataclass

from tetris.model.board import BoardState


# TODO: find or invent a way to do automatic delegation
@dataclass
class GameState:
    board_state: BoardState
    score: int

    @property
    def board(self):
        return self.board_state.board

    @property
    def piece_type(self):
        return self.board_state.piece_type

    @property
    def possible_moves(self):
        return self.board_state.possible_moves
    
    def get_piece_for_move(self, move):
        return self.board_state.get_piece_for_move(move)

    def play_move(self, move):
        return GameState(self.board_state.play_move(move), self.score + 1)
