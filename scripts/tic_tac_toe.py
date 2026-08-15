import os
import sys
import json
import re

DATA_FILE = "data/tic_tac_toe.json"
README_FILE = "README.md"

POS_MAP = {
    "top-left": 0, "top-mid": 1, "top-right": 2,
    "mid-left": 3, "mid-mid": 4, "mid-right": 5,
    "bot-left": 6, "bot-mid": 7, "bot-right": 8,
    "reset": -1
}

POS_NAMES = [
    "top-left", "top-mid", "top-right",
    "mid-left", "mid-mid", "mid-right",
    "bot-left", "bot-mid", "bot-right"
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "board": [" ", " ", " ", " ", " ", " ", " ", " ", " "],
        "turn": "X",
        "moves_played": 0,
        "games_completed": 0,
        "last_player": "None",
        "status": "New game ready! It's your turn (❌)."
    }

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def check_winner(board):
    wins = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ]
    for w in wins:
        if board[w[0]] != " " and board[w[0]] == board[w[1]] == board[w[2]]:
            return board[w[0]]
    if " " not in board:
        return "Draw"
    return None

def bot_move(board):
    # Try to win
    for i in range(9):
        if board[i] == " ":
            board[i] = "O"
            if check_winner(board) == "O":
                return i
            board[i] = " "

    # Try to block user
    for i in range(9):
        if board[i] == " ":
            board[i] = "X"
            if check_winner(board) == "X":
                board[i] = " "
                return i
            board[i] = " "

    # Center
    if board[4] == " ":
        return 4

    # Corners
    for i in [0, 2, 6, 8]:
        if board[i] == " ":
            return i

    # Sides
    for i in [1, 3, 5, 7]:
        if board[i] == " ":
            return i
    return -1

def generate_markdown_board(data):
    b = data["board"]
    user = "SparshGarg999"
    repo = "SparshGarg999"

    def cell(idx):
        val = b[idx]
        pos_name = POS_NAMES[idx]
        if val == "X":
            return "❌"
        elif val == "O":
            return "⭕"
        else:
            issue_title = f"ttc|move|{pos_name}"
            issue_body = f"Just+push+%27Submit+new+issue%27+without+editing+the+title.+The+game+bot+will+automatically+play+and+update+the+board!"
            url = f"https://github.com/{user}/{repo}/issues/new?title={issue_title}&body={issue_body}"
            return f"[`⬜`]({url})"

    reset_url = f"https://github.com/{user}/{repo}/issues/new?title=ttc|move|reset&body=Submit+issue+to+start+a+new+game!"

    md = []
    md.append(f"**Moves Played:** `{data['moves_played']}` &nbsp;|&nbsp; **Completed Games:** `{data['games_completed']}` &nbsp;|&nbsp; **Last Player:** `{data['last_player']}`\n")
    md.append(f"**Status:** {data['status']}\n")
    md.append("| Top | Mid | Right |")
    md.append("| :---: | :---: | :---: |")
    md.append(f"| {cell(0)} | {cell(1)} | {cell(2)} |")
    md.append(f"| {cell(3)} | {cell(4)} | {cell(5)} |")
    md.append(f"| {cell(6)} | {cell(7)} | {cell(8)} |\n")
    md.append(f"👉 *Click any empty square [`⬜`] to play as `❌`. [🔄 Reset Game]({reset_url})*")
    return "\n".join(md)

def update_readme(board_md):
    if not os.path.exists(README_FILE):
        return
    with open(README_FILE, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(r"<!-- TIC-TAC-TOE-START -->.*<!-- TIC-TAC-TOE-END -->", re.DOTALL)
    replacement = f"<!-- TIC-TAC-TOE-START -->\n{board_md}\n<!-- TIC-TAC-TOE-END -->"
    
    if pattern.search(content):
        new_content = pattern.sub(replacement, content)
        with open(README_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)

def main():
    if len(sys.argv) < 3:
        print("Usage: python tic_tac_toe.py <move> <player_username>")
        return

    move_arg = sys.argv[1].strip().lower()
    player = sys.argv[2].strip()

    data = load_data()
    data["last_player"] = f"@{player}"

    if move_arg == "reset":
        data["board"] = [" ", " ", " ", " ", " ", " ", " ", " ", " "]
        data["status"] = "New game started! It's your turn (❌)."
        save_data(data)
        update_readme(generate_markdown_board(data))
        print("Reset game.")
        return

    if move_arg not in POS_MAP:
        print(f"Unknown move: {move_arg}")
        return

    pos = POS_MAP[move_arg]
    if data["board"][pos] != " ":
        data["status"] = f"Square `{move_arg}` is already taken! Please pick another."
        save_data(data)
        update_readme(generate_markdown_board(data))
        return

    # User move (X)
    data["board"][pos] = "X"
    data["moves_played"] += 1

    winner = check_winner(data["board"])
    if winner:
        data["games_completed"] += 1
        if winner == "X":
            data["status"] = f"🎉 **@{player} won the game as ❌!** [Start New Game](https://github.com/SparshGarg999/SparshGarg999/issues/new?title=ttc|move|reset&body=Start+new+game)"
        elif winner == "Draw":
            data["status"] = f"🤝 **It's a Draw!** [Start New Game](https://github.com/SparshGarg999/SparshGarg999/issues/new?title=ttc|move|reset&body=Start+new+game)"
        save_data(data)
        update_readme(generate_markdown_board(data))
        return

    # Bot move (O)
    bot_pos = bot_move(data["board"])
    if bot_pos != -1:
        data["board"][bot_pos] = "O"
        data["moves_played"] += 1

    winner = check_winner(data["board"])
    if winner:
        data["games_completed"] += 1
        if winner == "O":
            data["status"] = f"🤖 **AI Assistant won as ⭕!** [Start New Game](https://github.com/SparshGarg999/SparshGarg999/issues/new?title=ttc|move|reset&body=Start+new+game)"
        elif winner == "Draw":
            data["status"] = f"🤝 **It's a Draw!** [Start New Game](https://github.com/SparshGarg999/SparshGarg999/issues/new?title=ttc|move|reset&body=Start+new+game)"
    else:
        data["status"] = "Game in progress. Your turn (❌)!"

    save_data(data)
    update_readme(generate_markdown_board(data))
    print(f"Processed move {move_arg} for player {player}")

if __name__ == "__main__":
    main()
