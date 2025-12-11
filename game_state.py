"""
Game State module: Tracks game state (turn, positions, move history),
supports saving/loading as JSON.
"""

from board import Board
from piece import pos_to_coords, coords_to_pos

class GameState:
    def __init__(self):
        self.board = Board()
        self.turn = 'w'  # 'w' or 'b'
        self.move_history = []  # List of {'from': 'e2', 'to': 'e4', 'piece': 'P', 'captured': 'p'}

    def reset(self):
        """Reset the game to initial state."""
        self.board.reset()
        self.turn = 'w'
        self.move_history = []

    def make_move(self, from_pos, to_pos):
        """Attempt to make a move. Returns (success, message)."""
        from_coords = pos_to_coords(from_pos)
        to_coords = pos_to_coords(to_pos)
        piece = self.board.get_piece(from_coords)
        if not piece:
            return False, "No piece at source."
        if piece.color != self.turn:
            return False, "Not your turn."
        legal_moves = piece.get_legal_moves(self.board)
        if to_coords not in legal_moves:
            return False, "Illegal move."
        captured = self.board.move_piece(from_coords, to_coords)
        # Pawn promotion (simple: always to Queen)
        if piece.code.upper() == 'P' and (to_coords[0] == 0 or to_coords[0] == 7):
            from piece import Queen
            self.board.set_piece(to_coords, Queen(piece.color, to_coords, 'Q' if piece.color == 'w' else 'q'))
        self.move_history.append({
            'from': coords_to_pos(from_coords),
            'to': coords_to_pos(to_coords),
            'piece': piece.code,
            'captured': captured.code if captured else None
        })
        self.turn = 'b' if self.turn == 'w' else 'w'
        return True, "Move made."

    def is_game_over(self):
        """Check if the game is over (simple: king captured)."""
        kings = [p for p in self.board.all_pieces() if p.code.upper() == 'K']
        return len(kings) < 2

    def to_dict(self):
        """Serialize game state for saving/loading."""
        return {
            'board': self.board.to_dict(),
            'turn': self.turn,
            'move_history': self.move_history
        }

    def from_dict(self, data):
        """Load game state from dict."""
        self.board.from_dict(data['board'])
        self.turn = data['turn']
        self.move_history = data['move_history']