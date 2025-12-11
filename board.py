"""
Board module: Defines the Board class for 8x8 chessboard,
initializes piece positions, handles updates, and reset.
"""

from piece import create_piece, Piece

class Board:
    def __init__(self):
        self.squares = [[None for _ in range(8)] for _ in range(8)]
        self.reset()

    def reset(self):
        """Initialize the board with standard chess starting positions."""
        # Place pieces for both colors
        setup = [
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],
            ['P'] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            [None] * 8,
            ['p'] * 8,
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r']
        ]
        for r in range(8):
            for c in range(8):
                code = setup[r][c]
                self.squares[r][c] = create_piece(code, (r, c)) if code else None

    def get_piece(self, pos):
        """Get piece at board position (row, col)."""
        r, c = pos
        return self.squares[r][c]

    def set_piece(self, pos, piece):
        """Set piece at board position (row, col)."""
        r, c = pos
        self.squares[r][c] = piece
        if piece:
            piece.position = (r, c)

    def move_piece(self, from_pos, to_pos):
        """Move piece from from_pos to to_pos."""
        piece = self.get_piece(from_pos)
        captured = self.get_piece(to_pos)
        self.set_piece(to_pos, piece)
        self.set_piece(from_pos, None)
        return captured

    def to_dict(self):
        """Return board as a serializable dict (for frontend)."""
        board_dict = []
        for r in range(8):
            row = []
            for c in range(8):
                piece = self.squares[r][c]
                row.append(piece.to_dict() if piece else None)
            board_dict.append(row)
        return board_dict

    def from_dict(self, board_dict):
        """Load board from dict."""
        for r in range(8):
            for c in range(8):
                pdata = board_dict[r][c]
                self.squares[r][c] = create_piece(pdata['code'], (r, c)) if pdata else None

    def all_pieces(self, color=None):
        """Yield all pieces, optionally filtered by color."""
        for r in range(8):
            for c in range(8):
                piece = self.squares[r][c]
                if piece and (color is None or piece.color == color):
                    yield piece

    def copy(self):
        """Return a deep copy of the board."""
        new_board = Board()
        new_board.squares = [[p.copy() if p else None for p in row] for row in self.squares]
        return new_board