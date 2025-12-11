"""
Flask main application for Chess Game with Coach.
Handles routes for UI, moves, AI, coach suggestions, save/load.
"""

import asyncio
import json
import os
from flask import Flask, render_template, request, jsonify, send_from_directory
from board import Board
from game_state import GameState
from ai import ChessAI
from coach import Coach

app = Flask(__name__, static_folder='static', template_folder='templates')

# Global game state (for demo; in production, use sessions or DB)
game_state = GameState()
ai = ChessAI()
coach = Coach()

GAMES_PATH = os.path.join(os.path.dirname(__file__), 'games', 'saved_games.json')

@app.route('/')
def index():
    """Serve the main chessboard UI."""
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    """
    Handle player move, validate, update state, get AI move and coach feedback.
    Expects JSON: {from: "e2", to: "e4", mode: "ai" or "human"}
    Returns: {success, board, move_history, ai_move, coach_feedback}
    """
    data = request.get_json()
    from_sq = data.get('from')
    to_sq = data.get('to')
    mode = data.get('mode', 'ai')
    player_color = game_state.turn

    # Validate and make player move
    valid, msg = game_state.make_move(from_sq, to_sq)
    if not valid:
        return jsonify({'success': False, 'message': msg, 'board': game_state.board.to_dict(), 'move_history': game_state.move_history})

    # Coach feedback on player's move
    feedback = asyncio.run(coach.analyze_move(game_state, from_sq, to_sq, player_color))

    ai_move = None
    # Only do AI move if mode is 'ai' and game is not over and it's now black's turn
    if mode == 'ai' and not game_state.is_game_over() and game_state.turn == 'b':
        ai_from, ai_to = asyncio.run(ai.get_best_move(game_state, depth=2))
        if ai_from and ai_to:
            game_state.make_move(ai_from, ai_to)
            ai_move = {'from': ai_from, 'to': ai_to}
            feedback += asyncio.run(coach.analyze_move(game_state, ai_from, ai_to, game_state.turn))

    return jsonify({
        'success': True,
        'board': game_state.board.to_dict(),
        'move_history': game_state.move_history,
        'ai_move': ai_move,
        'coach_feedback': feedback,
        'turn': game_state.turn
    })

@app.route('/save', methods=['POST'])
def save():
    """Save current game state to JSON file."""
    with open(GAMES_PATH, 'w') as f:
        json.dump(game_state.to_dict(), f)
    return jsonify({'success': True})


@app.route('/load', methods=['GET'])
def load():
    """Load game state from JSON file, or start new game if none exists."""
    if not os.path.exists(GAMES_PATH):
        game_state.reset()
        return jsonify({
            'success': True,
            'board': game_state.board.to_dict(),
            'move_history': game_state.move_history,
            'turn': game_state.turn
        })
    with open(GAMES_PATH, 'r') as f:
        try:
            data = json.load(f)
            if not data or 'board' not in data:
                game_state.reset()
            else:
                game_state.from_dict(data)
        except Exception:
            game_state.reset()
    return jsonify({
        'success': True,
        'board': game_state.board.to_dict(),
        'move_history': game_state.move_history,
        'turn': game_state.turn
    })

@app.route('/suggest', methods=['GET'])
def suggest():
    """Return coach suggestions for thought bubbles."""
    suggestions = asyncio.run(coach.get_suggestions(game_state))
    return jsonify({'suggestions': suggestions})

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files."""
    return send_from_directory(app.static_folder, filename)

if __name__ == '__main__':
    app.run(debug=True)