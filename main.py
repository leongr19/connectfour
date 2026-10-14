import sys
import tkinter as tk
import numpy as np
import time
import random

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

        #self.load_test_data()

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

    def load_test_data(self):
        self.board[5, 3] = 1
        self.board[0, 0] = 1
        self.board[1, 1] = 2
        self.board[2, 2] = 1
        self.board[3, 3] = 1
        self.board[4, 4] = 2
        self.board[5, 5] = 1
        self.board[5, 6] = 1

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
            x_center = (self.current_col * self.CELL_SIZE) + (self.CELL_SIZE//2)
            self.canvas.create_polygon(
                x_center, 15,
                x_center - 10, 2,
                x_center + 10, 2,
                fill="darkorange"
            )

    def check_col(self):
        if self.board[0, self.current_col] != 0:
            return False
        
        return True
            

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
            self.message.set("Bot (Yellow) it is your turn")
            self.root.after(1000, self.bot)

    def bot(self):
        col = random.randint(0, 6)

        print(col)

        self.current_col = col

        self.draw_board()

        self.root.after(300, self.press_enter)

    def check_winner(self):
        player = self.current_player

        for r in range(6):
            for c in range(4):
                if all(self.board[r, c+i] == player for i in range(4)):
                    return True
        
        for r in range(3):
            for c in range(7):
                if all(self.board[r+i, c] == player for i in range(4)):
                    return True

        for r in range(3):
            for c in range(4):
                if all(self.board[r+i, c+i] == player for i in range(4)):
                    return True

        for r in range(3, 6):
            for c in range(4):
                if all(self.board[r-i, c+i] == player for i in range(4)):
                    return True

        return False

        
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
            self.board[0, self.current_col] = self.current_player

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
            self.play()



if __name__ == "__main__":
    root = tk.Tk()
    app = ConnectFourGUI(root)
    print("Game Started")
    root.mainloop()