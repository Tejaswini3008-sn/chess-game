"""
Coach module: Analyzes player moves, identifies mistakes, and provides suggestions with explanations.
Returns JSON for thought bubbles.
"""

import asyncio
from ai import ChessAI
from piece import pos_to_coords, coords_to_pos

class Coach:
    def __init__(self):
        self.ai = ChessAI()
        self.last_feedback = []

    async def analyze_move(self, game_state, from_sq, to_sq, color):
        """
        Analyze the player's move, identify mistakes, and provide suggestions.
        Returns a list of feedback strings.
        """
        await asyncio.sleep(0.05)
        feedback = []
        # Simple mistake: moving into danger (piece can be captured next turn)
        from_coords = pos_to_coords(from_sq)
        to_coords = pos_to_coords(to_sq)
        piece = game_state.board.get_piece(to_coords)
        if not piece:
            return []
        # Check if the moved piece is now attacked
        opp_color = 'b' if color == 'w' else 'w'
        for opp_piece in game_state.board.all_pieces(opp_color):
            if to_coords in opp_piece.get_legal_moves(game_state.board):
                feedback.append(f"Careful! Your {self.piece_name(piece)} on {to_sq} can be captured.")
                break
        # Check if move exposes king
        king = next((p for p in game_state.board.all_pieces(color) if p.code.upper() == 'K'), None)
        if king:
            for opp_piece in game_state.board.all_pieces(opp_color):
                if king.position in opp_piece.get_legal_moves(game_state.board):
                    feedback.append("Warning: Your king is in danger!")
                    break
        # Suggest a better move (if any)
        best_from, best_to = await self.ai.get_best_move(game_state, depth=2)
        if best_from and best_to and (from_sq != best_from or to_sq != best_to):
            feedback.append(f"Try {self.move_hint(best_from, best_to)} next time for a stronger position.")
        self.last_feedback = feedback
        return feedback

    async def get_suggestions(self, game_state):
        """
        Return up to 3 suggestions for thought bubbles.
        """
        await asyncio.sleep(0.05)
        # If last feedback exists, use it; otherwise, suggest a move
        if self.last_feedback:
            return self.last_feedback[:3]
        color = game_state.turn
        best_from, best_to = await self.ai.get_best_move(game_state, depth=2)
        if best_from and best_to:
            return [f"Consider {self.move_hint(best_from, best_to)}!"]
        return ["Keep going!"]

    def piece_name(self, piece):
        """Return human-readable piece name."""
        names = {'P': 'pawn', 'N': 'knight', 'B': 'bishop', 'R': 'rook', 'Q': 'queen', 'K': 'king'}
        return names.get(piece.code.upper(), 'piece')

    def move_hint(self, from_sq, to_sq):
        """Return a hint string for a move."""
        return f"moving {from_sq} to {to_sq}"