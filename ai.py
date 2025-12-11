"""
AI module: Implements Minimax with Alpha-Beta pruning for computer moves.
Difficulty adjustable via search depth.
"""

import asyncio
import random
from copy import deepcopy
from piece import coords_to_pos

PIECE_VALUES = {'P': 1, 'N': 3, 'B': 3, 'R': 5, 'Q': 9, 'K': 1000}

class ChessAI:
    def __init__(self):
        pass

    async def get_best_move(self, game_state, depth=2):
        """Return best move (from_pos, to_pos) for current player using Minimax."""
        # Use asyncio.sleep to simulate async processing
        await asyncio.sleep(0.1)
        color = game_state.turn
        board = game_state.board.copy()
        best_score = float('-inf') if color == 'w' else float('inf')
        best_moves = []
        for piece in board.all_pieces(color):
            for move in piece.get_legal_moves(board):
                new_board = board.copy()
                new_board.move_piece(piece.position, move)
                score = self.minimax(new_board, depth - 1, float('-inf'), float('inf'), color == 'b')
                if (color == 'w' and score > best_score) or (color == 'b' and score < best_score):
                    best_score = score
                    best_moves = [(piece.position, move)]
                elif score == best_score:
                    best_moves.append((piece.position, move))
        if not best_moves:
            return None, None
        from_pos, to_pos = random.choice(best_moves)
        return coords_to_pos(from_pos), coords_to_pos(to_pos)

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        """Minimax with alpha-beta pruning."""
        if depth == 0 or self.is_game_over(board):
            return self.evaluate(board)
        color = 'w' if is_maximizing else 'b'
        if is_maximizing:
            max_eval = float('-inf')
            for piece in board.all_pieces(color):
                for move in piece.get_legal_moves(board):
                    new_board = board.copy()
                    new_board.move_piece(piece.position, move)
                    eval = self.minimax(new_board, depth - 1, alpha, beta, False)
                    max_eval = max(max_eval, eval)
                    alpha = max(alpha, eval)
                    if beta <= alpha:
                        break
            return max_eval
        else:
            min_eval = float('inf')
            for piece in board.all_pieces(color):
                for move in piece.get_legal_moves(board):
                    new_board = board.copy()
                    new_board.move_piece(piece.position, move)
                    eval = self.minimax(new_board, depth - 1, alpha, beta, True)
                    min_eval = min(min_eval, eval)
                    beta = min(beta, eval)
                    if beta <= alpha:
                        break
            return min_eval

    def evaluate(self, board):
        """Simple evaluation: sum of piece values."""
        score = 0
        for piece in board.all_pieces():
            val = PIECE_VALUES.get(piece.code.upper(), 0)
            score += val if piece.color == 'w' else -val
        return score

    def is_game_over(self, board):
        """Game over if one king left."""
        kings = [p for p in board.all_pieces() if p.code.upper() == 'K']
        return len(kings) < 2