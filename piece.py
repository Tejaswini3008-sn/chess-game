"""
Piece module: Defines Piece base class and subclasses for Pawn, Knight, Bishop, Rook, Queen, King.
Each piece implements legal move validation.
"""

def pos_to_coords(pos):
    """Convert algebraic notation (e.g., 'e4') to (row, col)."""
    if isinstance(pos, tuple):
        return pos
    col = ord(pos[0].lower()) - ord('a')
    row = 8 - int(pos[1])
    return (row, col)

def coords_to_pos(coords):
    """Convert (row, col) to algebraic notation (e.g., 'e4')."""
    row, col = coords
    return chr(col + ord('a')) + str(8 - row)

class Piece:
    def __init__(self, color, position, code):
        self.color = color  # 'w' or 'b'
        self.position = position  # (row, col)
        self.code = code  # 'P', 'N', etc.

    def get_legal_moves(self, board):
        """Return list of legal moves [(row, col), ...] for this piece."""
        return []

    def to_dict(self):
        """Serialize piece for frontend."""
        return {'color': self.color, 'code': self.code}

    def copy(self):
        """Return a copy of the piece."""
        return create_piece(self.code, self.position)

class Pawn(Piece):
    def get_legal_moves(self, board):
        moves = []
        r, c = self.position
        direction = -1 if self.color == 'w' else 1
        start_row = 6 if self.color == 'w' else 1
        # Forward move
        if 0 <= r + direction < 8 and not board.get_piece((r + direction, c)):
            moves.append((r + direction, c))
            # Double move from start
            if r == start_row and not board.get_piece((r + 2 * direction, c)):
                moves.append((r + 2 * direction, c))
        # Captures
        for dc in [-1, 1]:
            nc = c + dc
            nr = r + direction
            if 0 <= nc < 8 and 0 <= nr < 8:
                target = board.get_piece((nr, nc))
                if target and target.color != self.color:
                    moves.append((nr, nc))
        return moves

class Knight(Piece):
    def get_legal_moves(self, board):
        moves = []
        r, c = self.position
        for dr, dc in [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < 8 and 0 <= nc < 8:
                target = board.get_piece((nr, nc))
                if not target or target.color != self.color:
                    moves.append((nr, nc))
        return moves

class Bishop(Piece):
    def get_legal_moves(self, board):
        moves = []
        r, c = self.position
        for dr, dc in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = board.get_piece((nr, nc))
                if not target:
                    moves.append((nr, nc))
                elif target.color != self.color:
                    moves.append((nr, nc))
                    break
                else:
                    break
                nr += dr
                nc += dc
        return moves

class Rook(Piece):
    def get_legal_moves(self, board):
        moves = []
        r, c = self.position
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            while 0 <= nr < 8 and 0 <= nc < 8:
                target = board.get_piece((nr, nc))
                if not target:
                    moves.append((nr, nc))
                elif target.color != self.color:
                    moves.append((nr, nc))
                    break
                else:
                    break
                nr += dr
                nc += dc
        return moves

class Queen(Piece):
    def get_legal_moves(self, board):
        # Queen combines rook and bishop moves
        return Rook(self.color, self.position, self.code).get_legal_moves(board) + \
               Bishop(self.color, self.position, self.code).get_legal_moves(board)

class King(Piece):
    def get_legal_moves(self, board):
        moves = []
        r, c = self.position
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    target = board.get_piece((nr, nc))
                    if not target or target.color != self.color:
                        moves.append((nr, nc))
        return moves

def create_piece(code, position):
    """Factory for creating pieces from code."""
    if not code:
        return None
    color = 'w' if code.isupper() else 'b'
    code_upper = code.upper()
    if code_upper == 'P':
        return Pawn(color, position, code)
    elif code_upper == 'N':
        return Knight(color, position, code)
    elif code_upper == 'B':
        return Bishop(color, position, code)
    elif code_upper == 'R':
        return Rook(color, position, code)
    elif code_upper == 'Q':
        return Queen(color, position, code)
    elif code_upper == 'K':
        return King(color, position, code)
    else:
        return None