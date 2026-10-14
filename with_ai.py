import sys
import tkinter as tk
import numpy as np
import time
import random
import math


class ConnectFourGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect Four")
        self.root.resizable(False, False)

        self.board = np.zeros((6, 7), dtype=int)

        self.current_col = 3
        self.current_player = 0
        self.message = tk.StringVar(value="")
        self.game_over = False

        self.AI_DEPTH = 4

        self.CELL_SIZE = 80
        self.canvas = tk.Canvas(
            root,
            width=7 * self.CELL_SIZE,
            height=6 * self.CELL_SIZE,
            bg="blue",
        )
        self.canvas.pack()

        self.status_label = tk.Label(
            root,
            text="",
            font=("Arial", 16, "bold"),
            bg="black",
            fg="red",
            height=2,
            textvariable=self.message
        )
        self.status_label.pack(fill=tk.X)

        self.root.bind("<Left>", lambda e: self.move(-1))
        self.root.bind("a", lambda e: self.move(-1))

        self.root.bind("<Right>", lambda e: self.move(1))
        self.root.bind("d", lambda e: self.move(1))

        self.root.bind("<Return>", lambda e: self.press_enter())
        self.root.bind("<Escape>", lambda e: root.destroy())

        self.message.set("Game Started")

        self.draw_board()
        self.begin_to_play()

    def check_physic(self):
        for row in range(6):
            for col in range(7):
                if self.board[row, col] != 0:
                    row2 = row + 1
                    if row2 < 6 and row2 >= 0:
                        if self.board[row2, col] == 0:
                            self.board[row2, col] = self.board[row, col]
                            self.board[row, col] = 0

    def draw_board(self):
        self.canvas.delete("all")
        self.check_physic()

        for row in range(6):
            for col in range(7):
                x1 = col * self.CELL_SIZE + 5
                y1 = row * self.CELL_SIZE + 5
                x2 = (col + 1) * self.CELL_SIZE - 5
                y2 = (row + 1) * self.CELL_SIZE - 5

                if self.board[row, col] == 1:
                    farbe = "red"
                elif self.board[row, col] == 2:
                    farbe = "yellow"
                else:
                    farbe = "white"

                self.canvas.create_oval(x1, y1, x2, y2, fill=farbe, outline="black", width=2)

        if not self.game_over:
            x_center = (self.current_col * self.CELL_SIZE) + (self.CELL_SIZE // 2)
            self.canvas.create_polygon(
                x_center, 15,
                x_center - 10, 2,
                x_center + 10, 2,
                fill="darkorange"
            )

    def check_col(self):
        return int(self.board[0, self.current_col]) == 0

    def switch_player(self):
        if self.game_over:
            return

        if self.current_player == 1:
            self.current_player = 2
        else:
            self.current_player = 1

        self.play()

    def begin_to_play(self):
        if self.current_player == 0:
            if random.randint(1, 2) == 1:
                self.current_player = 1
            else:
                self.current_player = 2
        self.play()

    def play(self):
        if self.current_player == 1:
            self.status_label.config(fg="red")
            self.message.set("Player 1 (Red) it is your turn")
        elif self.current_player == 2:
            self.status_label.config(fg="yellow")
            self.message.set("Bot (Yellow) is thinking...")
            self.root.after(500, self.bot)

    def get_valid_locations(self, board):
        return [c for c in range(7) if int(board[0, c]) == 0]

    def get_next_open_row(self, board, col):
        for r in range(5, -1, -1):
            if int(board[r, col]) == 0:
                return r
        return -1

    def evaluate_window(self, window, piece):
        score = 0
        opp_piece = 1 if piece == 2 else 2

        if window.count(piece) == 4:
            score += 100000
        elif window.count(piece) == 3 and window.count(0) == 1:
            score += 10
        elif window.count(piece) == 2 and window.count(0) == 2:
            score += 3

        if window.count(opp_piece) == 3 and window.count(0) == 1:
            score -= 80

        return score

    def score_position(self, board, piece):
        score = 0

        center_array = [int(x) for x in board[:, 3]]
        center_count = center_array.count(piece)
        score += center_count * 4

        for r in range(6):
            row_array = [int(x) for x in board[r, :]]
            for c in range(4):
                window = row_array[c:c + 4]
                score += self.evaluate_window(window, piece)

        for c in range(7):
            col_array = [int(x) for x in board[:, c]]
            for r in range(3):
                window = col_array[r:r + 4]
                score += self.evaluate_window(window, piece)

        for r in range(3):
            for c in range(4):
                window = [int(board[r + i, c + i]) for i in range(4)]
                score += self.evaluate_window(window, piece)

        for r in range(3, 6):
            for c in range(4):
                window = [int(board[r - i, c + i]) for i in range(4)]
                score += self.evaluate_window(window, piece)

        return score

    def is_terminal_node(self, board):
        return (self.check_winner_static(board, 1) or
                self.check_winner_static(board, 2) or
                len(self.get_valid_locations(board)) == 0)

    def check_winner_static(self, board, player):
        for r in range(6):
            for c in range(4):
                if all(int(board[r, c + i]) == player for i in range(4)): return True
        for r in range(3):
            for c in range(7):
                if all(int(board[r + i, c]) == player for i in range(4)): return True
        for r in range(3):
            for c in range(4):
                if all(int(board[r + i, c + i]) == player for i in range(4)): return True
        for r in range(3, 6):
            for c in range(4):
                if all(int(board[r - i, c + i]) == player for i in range(4)): return True
        return False

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        valid_locations = self.get_valid_locations(board)
        is_terminal = self.is_terminal_node(board)

        if depth == 0 or is_terminal:
            if is_terminal:
                if self.check_winner_static(board, 2):
                    return (None, 100000000000000)
                elif self.check_winner_static(board, 1):
                    return (None, -100000000000000)
                else:
                    return (None, 0)
            else:
                return (None, self.score_position(board, 2))

        if maximizingPlayer:
            value = -math.inf
            column = random.choice(valid_locations) if valid_locations else 0
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                b_copy[row, col] = 2
                _, new_score = self.minimax(b_copy, depth - 1, alpha, beta, False)
                if new_score > value:
                    value = new_score
                    column = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return column, value

        else:
            value = math.inf
            column = random.choice(valid_locations) if valid_locations else 0
            for col in valid_locations:
                row = self.get_next_open_row(board, col)
                b_copy = board.copy()
                b_copy[row, col] = 1
                _, new_score = self.minimax(b_copy, depth - 1, alpha, beta, True)
                if new_score < value:
                    value = new_score
                    column = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return column, value

    def bot(self):
        if self.game_over:
            return

        col, minimax_score = self.minimax(self.board, self.AI_DEPTH, -math.inf, math.inf, True)

        if col is not None:
            self.current_col = col

        self.draw_board()
        self.root.after(200, self.press_enter)

    def check_winner(self):
        return self.check_winner_static(self.board, self.current_player)

    def move(self, value):
        if self.current_player == 2 or self.game_over:
            return

        self.current_col += value

        if self.current_col > 6:
            self.current_col = 0
        elif self.current_col < 0:
            self.current_col = 6

        self.draw_board()

    def press_enter(self):
        if self.game_over:
            return

        if self.check_col():
            target_row = self.get_next_open_row(self.board, self.current_col)
            self.board[target_row, self.current_col] = self.current_player

            self.draw_board()

            if self.check_winner():
                self.game_over = True
                self.draw_board()
                if self.current_player == 1:
                    self.status_label.config(fg="red")
                    self.message.set("GAME OVER - Player 1 (Red) Wins! (ESC to quit)")
                else:
                    self.status_label.config(fg="yellow")
                    self.message.set("GAME OVER - Bot (Yellow) Wins! (ESC to quit)")

            elif not np.any(self.board == 0):
                self.game_over = True
                self.status_label.config(fg="white")
                self.message.set("GAME OVER - Draw! (ESC to Quit)")

            else:
                self.switch_player()
        else:
            if self.current_player == 2:
                self.play()


#if __name__ == "main":
root = tk.Tk()
app = ConnectFourGUI(root)
print("Game Started")
root.mainloop()
