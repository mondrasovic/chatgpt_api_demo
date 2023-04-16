from __future__ import annotations

import abc
import functools
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.controller import Controller


class View(abc.ABC):
    def __init__(self) -> None:
        self.controller = None

    @property
    @abc.abstractmethod
    def temperature(self) -> float:
        pass

    @property
    @abc.abstractmethod
    def presence_penalty(self) -> float:
        pass

    @property
    @abc.abstractmethod
    def frequency_penalty(self) -> float:
        pass

    @property
    @abc.abstractmethod
    def top_probability(self) -> float:
        pass

    @abc.abstractmethod
    def add_message(self, role: str, content: str) -> None:
        pass

    @abc.abstractmethod
    def clear_history(self) -> None:
        pass

    @abc.abstractmethod
    def main_loop(self) -> None:
        pass

    def set_controller(self, controller: Controller) -> None:
        self.controller = controller


class ChatBotView(View):
    def __init__(self, master: tk.Misc, title: str = "ChatGPT API Demonstration") -> None:
        super().__init__()

        self.master = master
        self.master.title(title)

        self.history_text = tk.Text(self.master)
        self.prompt_text = tk.Text(self.master)
        self.prompt_text.bind("<KeyRelease>", self._on_prompt_text_key_release)
        self.send_prompt_button = tk.Button(
            self.master, text="Send prompt", command=self._on_send_prompt, state=tk.DISABLED
        )
        settings_frame = self._create_settings_frame(self.master)

        self.history_text.grid(row=0, column=0, rowspan=1, columnspan=2, sticky=tk.NSEW)
        self.prompt_text.grid(row=1, column=0, rowspan=1, columnspan=1)
        settings_frame.grid(
            row=1, column=1, rowspan=1, columnspan=1, padx=5, pady=5, sticky=tk.NSEW
        )
        self.send_prompt_button.grid(row=2, column=0, rowspan=1, columnspan=1, sticky=tk.NSEW)

    @property
    def temperature(self) -> float:
        return self.temperature_var.get()

    @property
    def presence_penalty(self) -> float:
        return self.presence_penalty_var.get()

    @property
    def frequency_penalty(self) -> float:
        return self.frequency_penalty_var.get()

    @property
    def top_probability(self) -> float:
        return self.top_probability_var.get()

    def add_message(self, role: str, content: str) -> None:
        self.history_text.configure(state=tk.NORMAL)

        self.history_text.insert(tk.END, f"\n{role.upper()}:\n")
        self.history_text.insert(tk.END, content + "\n")

        self.history_text.configure(state=tk.DISABLED)

    def clear_history(self) -> None:
        self.history_text.configure(state=tk.NORMAL)
        self.history_text.delete("1.0", tk.END)
        self.history_text.configure(state=tk.DISABLED)
        self._update_buttons_state()

    def main_loop(self) -> None:
        self.master.mainloop()

    def _create_settings_frame(self, master: tk.Misc) -> tk.Frame:
        frame = tk.Frame(master)

        self.selected_role_var = tk.StringVar()
        role_label = tk.Label(frame, text="Role:")
        system_role_radio_button = tk.Radiobutton(
            frame, text="system", variable=self.selected_role_var, value="system"
        )
        user_role_radio_button = tk.Radiobutton(
            frame, text="user", variable=self.selected_role_var, value="user"
        )

        horizontal_separator_1 = ttk.Separator(frame, orient="horizontal")
        horizontal_separator_2 = ttk.Separator(frame, orient="horizontal")

        self.temperature_var = tk.DoubleVar()
        self.presence_penalty_var = tk.DoubleVar()
        self.frequency_penalty_var = tk.DoubleVar()
        self.top_probability_var = tk.DoubleVar()

        create_scale = functools.partial(
            tk.Scale, master=frame, orient=tk.HORIZONTAL, resolution=0.05
        )

        temperature_label = tk.Label(frame, text="Temperature:")
        temperature_scale = create_scale(from_=0, to=2, variable=self.temperature_var)

        presence_penalty_label = tk.Label(frame, text="Presence penalty:")
        presence_penalty_scale = create_scale(from_=-2, to=2, variable=self.presence_penalty_var)

        frequency_penalty_label = tk.Label(frame, text="Frequency penalty:")
        frequency_penalty_scale = create_scale(from_=-2, to=2, variable=self.frequency_penalty_var)

        top_probability_label = tk.Label(frame, text="Top probability:")
        top_probabitliy_scale = create_scale(from_=0, to=1, variable=self.top_probability_var)

        self.clear_prompt_button = tk.Button(
            frame, text="Clear prompt", command=self._on_clear_prompt, state=tk.DISABLED
        )
        self.clear_history_button = tk.Button(
            frame, text="Clear history", command=self._on_clear_history, state=tk.DISABLED
        )

        self.selected_role_var.set("system")
        self.temperature_var.set(1.0)
        self.presence_penalty_var.set(0.0)
        self.frequency_penalty_var.set(0.0)
        self.top_probability_var.set(1.0)

        separator_padding = 10

        role_label.grid(row=0, column=0, rowspan=1, columnspan=1, sticky=tk.W)
        system_role_radio_button.grid(row=0, column=1, rowspan=1, columnspan=1)
        user_role_radio_button.grid(row=0, column=2, rowspan=1, columnspan=1)

        horizontal_separator_1.grid(
            row=1, column=0, rowspan=1, columnspan=3, pady=separator_padding, sticky=tk.NSEW
        )

        temperature_label.grid(row=2, column=0, rowspan=1, columnspan=1, sticky=tk.W)
        temperature_scale.grid(row=2, column=1, rowspan=1, columnspan=2, sticky=tk.NSEW)

        presence_penalty_label.grid(row=3, column=0, rowspan=1, columnspan=1, sticky=tk.W)
        presence_penalty_scale.grid(row=3, column=1, rowspan=1, columnspan=2, sticky=tk.NSEW)

        frequency_penalty_label.grid(row=4, column=0, rowspan=1, columnspan=1, sticky=tk.W)
        frequency_penalty_scale.grid(row=4, column=1, rowspan=1, columnspan=2, sticky=tk.NSEW)

        top_probability_label.grid(row=5, column=0, rowspan=1, columnspan=1, sticky=tk.W)
        top_probabitliy_scale.grid(row=5, column=1, rowspan=1, columnspan=2, sticky=tk.NSEW)

        horizontal_separator_2.grid(
            row=6, column=0, rowspan=1, columnspan=3, pady=separator_padding, sticky=tk.NSEW
        )

        self.clear_prompt_button.grid(row=7, column=0, rowspan=1, columnspan=3, sticky=tk.NSEW)
        self.clear_history_button.grid(row=8, column=0, rowspan=1, columnspan=3, sticky=tk.NSEW)

        return frame

    def _on_send_prompt(self) -> None:
        prompt_content = self.prompt_text.get("1.0", tk.END).strip()
        self._clear_prompt()

        self.controller.handle_prompt_message(self.selected_role_var.get(), prompt_content)
        self._update_buttons_state()

    def _on_clear_prompt(self) -> None:
        self._clear_prompt()

    def _on_clear_history(self) -> None:
        self.controller.clear_history()

    def _on_prompt_text_key_release(self, _) -> None:
        self._update_buttons_state()

    def _clear_prompt(self) -> None:
        self.prompt_text.delete("1.0", tk.END)
        self._update_buttons_state()

    def _update_buttons_state(self) -> None:
        prompt_button_state = self.get_button_state_for_text_area(self.prompt_text)
        history_button_state = self.get_button_state_for_text_area(self.history_text)

        self.send_prompt_button.config(state=prompt_button_state)
        self.clear_prompt_button.config(state=prompt_button_state)
        self.clear_history_button.config(state=history_button_state)

    @staticmethod
    def get_button_state_for_text_area(text_widget: tk.Text) -> bool:
        return tk.NORMAL if text_widget.get("1.0", tk.END).strip() else tk.DISABLED
