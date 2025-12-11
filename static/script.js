// Chess Game Frontend: Play vs Human or AI, Coach toggle, highlights possible moves

const boardElem = document.getElementById('chessboard');
const moveListElem = document.getElementById('move-list');
const bubblesElem = document.getElementById('thought-bubbles');
const undoBtn = document.getElementById('undo-btn');
const saveBtn = document.getElementById('save-btn');
const loadBtn = document.getElementById('load-btn');
const resetBtn = document.getElementById('reset-btn');
const modeSelect = document.getElementById('mode-select');
const coachToggle = document.getElementById('coach-toggle');

let boardState = [];
let moveHistory = [];
let selected = null;
let lastMove = null;
let currentTurn = 'w'; // 'w' or 'b'
let mode = modeSelect ? modeSelect.value : 'ai'; // 'ai' or 'human'
let legalMoves = [];

const PIECE_UNICODE = {
    'wP': '♙', 'wN': '♘', 'wB': '♗', 'wR': '♖', 'wQ': '♕', 'wK': '♔',
    'bP': '♟', 'bN': '♞', 'bB': '♝', 'bR': '♜', 'bQ': '♛', 'bK': '♚'
};

function posToCoords(pos) {
    const col = pos.charCodeAt(0) - 'a'.charCodeAt(0);
    const row = 8 - parseInt(pos[1]);
    return [row, col];
}

function coordsToPos(row, col) {
    return String.fromCharCode('a'.charCodeAt(0) + col) + (8 - row);
}

function renderBoard() {
    boardElem.innerHTML = '';
    for (let r = 0; r < 8; r++) {
        for (let c = 0; c < 8; c++) {
            const square = document.createElement('div');
            square.className = 'square ' + ((r + c) % 2 === 0 ? 'light' : 'dark');
            square.dataset.row = r;
            square.dataset.col = c;
            if (selected && selected[0] === r && selected[1] === c) {
                square.classList.add('selected');
            }
            if (legalMoves.some(([mr, mc]) => mr === r && mc === c)) {
                square.classList.add('move-target');
            }
            if (lastMove && ((lastMove.from[0] === r && lastMove.from[1] === c) || (lastMove.to[0] === r && lastMove.to[1] === c))) {
                square.classList.add('last-move');
            }
            const piece = boardState[r][c];
            if (piece) {
                const span = document.createElement('span');
                span.className = 'piece';
                span.textContent = PIECE_UNICODE[piece.color + piece.code.toUpperCase()];
                square.appendChild(span);
            }
            square.addEventListener('click', () => onSquareClick(r, c));
            boardElem.appendChild(square);
        }
    }
}

function renderMoveHistory() {
    moveListElem.innerHTML = '';
    for (let i = 0; i < moveHistory.length; i += 2) {
        const li = document.createElement('li');
        let text = moveHistory[i].piece.toUpperCase() + ': ' + moveHistory[i].from + '-' + moveHistory[i].to;
        if (moveHistory[i].captured) text += ' x' + moveHistory[i].captured.toUpperCase();
        if (moveHistory[i + 1]) {
            text += ' | ' + moveHistory[i + 1].piece.toUpperCase() + ': ' + moveHistory[i + 1].from + '-' + moveHistory[i + 1].to;
            if (moveHistory[i + 1].captured) text += ' x' + moveHistory[i + 1].captured.toUpperCase();
        }
        li.textContent = text;
        moveListElem.appendChild(li);
    }
}

// Helper: get legal moves for a piece at (r, c)
function getLegalMoves(r, c) {
    const piece = boardState[r][c];
    if (!piece) return [];
    let moves = [];
    // Pawn
    if (piece.code.toUpperCase() === 'P') {
        let dir = piece.color === 'w' ? -1 : 1;
        let startRow = piece.color === 'w' ? 6 : 1;
        // Forward
        if (inBounds(r + dir, c) && !boardState[r + dir][c]) {
            moves.push([r + dir, c]);
            if (r === startRow && !boardState[r + 2 * dir][c]) {
                moves.push([r + 2 * dir, c]);
            }
        }
        // Captures
        for (let dc of [-1, 1]) {
            let nr = r + dir, nc = c + dc;
            if (inBounds(nr, nc) && boardState[nr][nc] && boardState[nr][nc].color !== piece.color) {
                moves.push([nr, nc]);
            }
        }
    }
    // Knight
    else if (piece.code.toUpperCase() === 'N') {
        for (let [dr, dc] of [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]]) {
            let nr = r + dr, nc = c + dc;
            if (inBounds(nr, nc) && (!boardState[nr][nc] || boardState[nr][nc].color !== piece.color)) {
                moves.push([nr, nc]);
            }
        }
    }
    // Bishop
    else if (piece.code.toUpperCase() === 'B') {
        for (let [dr, dc] of [[-1, -1], [-1, 1], [1, -1], [1, 1]]) {
            let nr = r + dr, nc = c + dc;
            while (inBounds(nr, nc)) {
                if (!boardState[nr][nc]) {
                    moves.push([nr, nc]);
                } else {
                    if (boardState[nr][nc].color !== piece.color) moves.push([nr, nc]);
                    break;
                }
                nr += dr; nc += dc;
            }
        }
    }
    // Rook
    else if (piece.code.toUpperCase() === 'R') {
        for (let [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
            let nr = r + dr, nc = c + dc;
            while (inBounds(nr, nc)) {
                if (!boardState[nr][nc]) {
                    moves.push([nr, nc]);
                } else {
                    if (boardState[nr][nc].color !== piece.color) moves.push([nr, nc]);
                    break;
                }
                nr += dr; nc += dc;
            }
        }
    }
    // Queen
    else if (piece.code.toUpperCase() === 'Q') {
        // Rook + Bishop
        moves = moves.concat(getLegalMovesForType(r, c, 'R'));
        moves = moves.concat(getLegalMovesForType(r, c, 'B'));
    }
    // King
    else if (piece.code.toUpperCase() === 'K') {
        for (let dr = -1; dr <= 1; dr++) {
            for (let dc = -1; dc <= 1; dc++) {
                if (dr === 0 && dc === 0) continue;
                let nr = r + dr, nc = c + dc;
                if (inBounds(nr, nc) && (!boardState[nr][nc] || boardState[nr][nc].color !== piece.color)) {
                    moves.push([nr, nc]);
                }
            }
        }
    }
    return moves;
}

// Helper for Queen moves
function getLegalMovesForType(r, c, type) {
    const piece = boardState[r][c];
    let moves = [];
    if (type === 'R') {
        for (let [dr, dc] of [[-1, 0], [1, 0], [0, -1], [0, 1]]) {
            let nr = r + dr, nc = c + dc;
            while (inBounds(nr, nc)) {
                if (!boardState[nr][nc]) {
                    moves.push([nr, nc]);
                } else {
                    if (boardState[nr][nc].color !== piece.color) moves.push([nr, nc]);
                    break;
                }
                nr += dr; nc += dc;
            }
        }
    } else if (type === 'B') {
        for (let [dr, dc] of [[-1, -1], [-1, 1], [1, -1], [1, 1]]) {
            let nr = r + dr, nc = c + dc;
            while (inBounds(nr, nc)) {
                if (!boardState[nr][nc]) {
                    moves.push([nr, nc]);
                } else {
                    if (boardState[nr][nc].color !== piece.color) moves.push([nr, nc]);
                    break;
                }
                nr += dr; nc += dc;
            }
        }
    }
    return moves;
}

function inBounds(r, c) {
    return r >= 0 && r < 8 && c >= 0 && c < 8;
}

function onSquareClick(r, c) {
    const piece = boardState[r][c];
    // Only allow selecting a piece of the current turn
    if (selected) {
        // Try move
        if (!(selected[0] === r && selected[1] === c)) {
            // Only allow move if it's a legal move
            if (legalMoves.some(([mr, mc]) => mr === r && mc === c)) {
                const from = coordsToPos(selected[0], selected[1]);
                const to = coordsToPos(r, c);
                makeMove(from, to);
                selected = null;
                legalMoves = [];
                renderBoard();
                return;
            }
        }
        // Deselect
        selected = null;
        legalMoves = [];
    } else if (piece && piece.color === currentTurn) {
        selected = [r, c];
        legalMoves = getLegalMoves(r, c);
    }
    renderBoard();
}

async function makeMove(from, to) {
    const coachEnabled = coachToggle && coachToggle.checked;
    const res = await fetch('/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({from, to, mode})
    });
    const data = await res.json();
    if (!data.success) {
        if (coachEnabled) showCoachBubbles([data.message]);
        return;
    }
    boardState = data.board;
    moveHistory = data.move_history;
    lastMove = {from: posToCoords(from), to: posToCoords(to)};
    currentTurn = data.turn || (currentTurn === 'w' ? 'b' : 'w');
    selected = null;
    legalMoves = [];
    renderBoard();
    renderMoveHistory();
    if (coachEnabled) showCoachBubbles(data.coach_feedback);

    // If mode is AI and it's black's turn, let AI move (handled by backend, so no need to call makeAIMove)
}


async function makeAIMove() {
    // Ask backend for AI move by making a dummy move (AI will move for black)
    const res = await fetch('/move', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({from: null, to: null, ai: true, mode})
    });
    const data = await res.json();
    if (data.success) {
        boardState = data.board;
        moveHistory = data.move_history;
        lastMove = data.last_ai_move
            ? {from: posToCoords(data.last_ai_move.from), to: posToCoords(data.last_ai_move.to)}
            : null;
        currentTurn = 'w';
        selected = null;
        legalMoves = [];
        renderBoard();
        renderMoveHistory();
        if (coachToggle && coachToggle.checked) showCoachBubbles(data.coach_feedback);
    }
}

function showCoachBubbles(messages) {
    if (coachToggle && !coachToggle.checked) return;
    while (bubblesElem.firstChild) {
        bubblesElem.removeChild(bubblesElem.firstChild);
    }
    if (!messages) return;
    messages.slice(0, 3).forEach((msg, idx) => {
        const bubble = document.createElement('div');
        bubble.className = 'thought-bubble';
        bubble.textContent = msg;
        bubblesElem.appendChild(bubble);
        setTimeout(() => {
            if (bubble.parentNode) bubble.parentNode.removeChild(bubble);
        }, 5000);
    });
}

async function fetchCoachSuggestions() {
    if (coachToggle && !coachToggle.checked) return;
    const res = await fetch('/suggest');
    const data = await res.json();
    showCoachBubbles(data.suggestions);
}

async function fetchBoard() {
    const res = await fetch('/load');
    const data = await res.json();
    if (data.success) {
        boardState = data.board;
        moveHistory = data.move_history;
        currentTurn = data.turn || 'w';
        selected = null;
        legalMoves = [];
        renderBoard();
        renderMoveHistory();
        fetchCoachSuggestions();
    } else {
        await resetGame();
    }
}

async function resetGame() {
    await fetch('/load');
    location.reload();
}

undoBtn.addEventListener('click', () => {
    location.reload(); // Simple undo: reload for now
});

saveBtn.addEventListener('click', async () => {
    await fetch('/save', {method: 'POST'});
    showCoachBubbles(["Game saved!"]);
});

loadBtn.addEventListener('click', async () => {
    await fetchBoard();
    showCoachBubbles(["Game loaded!"]);
});

resetBtn.addEventListener('click', async () => {
    await resetGame();
});

if (modeSelect) {
    modeSelect.addEventListener('change', () => {
        mode = modeSelect.value;
        resetGame();
    });
}

if (coachToggle) {
    coachToggle.addEventListener('change', () => {
        if (!coachToggle.checked) {
            while (bubblesElem.firstChild) {
                bubblesElem.removeChild(bubblesElem.firstChild);
            }
        } else {
            fetchCoachSuggestions();
        }
    });
}

window.addEventListener('DOMContentLoaded', async () => {
    mode = modeSelect ? modeSelect.value : 'ai';
    await fetchBoard();
    setInterval(fetchCoachSuggestions, 7000);
});