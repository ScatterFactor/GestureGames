import tkinter as tk
from tkinter import ttk, messagebox
from ttkthemes import ThemedTk
from knight import knight
from jungle import jungle
from rps import rps
from snake import snake
from videogame import videogame


def jungle_main():
    window.destroy()
    jungle.run()


def knight_main():
    window.destroy()
    knight.run()


def rps_main():
    window.destroy()
    a = rps.RPS()


def snake_main():
    window.destroy()
    snake.run()


def videogame_main():
    window.destroy()
    videogame.run()


def main_menu():
    global window
    window = ThemedTk(theme="arc")  # 使用 ttkthemes 库提供的主题

    window.title("menu")

    label = ttk.Label(window, text="MENU", font=("Helvetica", 16))
    label.pack(pady=10)

    style = ttk.Style()
    style.configure("TButton", font=("Helvetica", 12), padding=10)

    buttons = [
        ("jungle adventure", jungle_main),
        ("knight run", knight_main),
        ("rock paper scissors", rps_main),
        ("snake", snake_main),
        ("video game", videogame_main),
    ]

    for text, command in buttons:
        button = ttk.Button(window, text=text, command=command, width=20)
        button.pack(pady=5)

    window.mainloop()


if __name__ == "__main__":
    main_menu()
