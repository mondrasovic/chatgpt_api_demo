from __future__ import annotations

import tkinter as tk

from app.controller import ChatBotController
from app.model import ChatBotModel
from app.view import ChatBotView


def main() -> None:
    main_window = tk.Tk()
    model = ChatBotModel()
    view = ChatBotView(main_window)
    ChatBotController(model, view)
    view.main_loop()


if __name__ == "__main__":
    main()
