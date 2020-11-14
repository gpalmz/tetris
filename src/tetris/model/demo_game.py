from .game import (
    Piece, 
    PieceType, 
    PieceOrientation, 
    State, 
    create_initial_board,
)

# demo piece
piece_0 = Piece(PieceType.L, PieceOrientation.UP)
print(piece_0)
print(piece_0.rotated_90_cw(rotation_count=1))
print(piece_0.block_coords)

# demo gameplay
board_0 = create_initial_board()

state_0 = State(board_0, PieceType.L)
possible_moves_0 = state_0.possible_moves
for move in possible_moves_0:
    print(move)

state_1 = state_0.play_move(possible_moves_0[-1])
print(state_1.board)

possible_moves_1 = state_1.possible_moves
state_2 = state_1.play_move(possible_moves_1[-1])
print(state_2.board)
