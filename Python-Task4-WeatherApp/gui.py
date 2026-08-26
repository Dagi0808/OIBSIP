"""Tkinter GUI for the Weather App."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import font as tkfont
from tkinter import ttk

from utils import (
    format_temp,
    format_wind,
    epoch_to_time,
    load_icon,
    load_small_icon,
    parse_current,
    parse_daily,
    parse_hourly,
)
from weather import detect_city_from_ip, get_current_weather, get_forecast

# ── Colour palette ──────────────────────────────────────────────────────────
DARK = {
    "bg":        "#1a1a2e",
    "panel":     "#16213e",
    "card":      "#0f3460",
    "accent":    "#e94560",
    "text":      "#eaeaea",
    "muted":     "#a0aec0",
    "input_bg":  "#0f3460",
    "btn":       "#e94560",
    "btn_hover": "#c73652",
}

LIGHT = {
    "bg":        "#e8f4fd",
    "panel":     "#ffffff",
    "card":      "#dbeafe",
    "accent":    "#2563eb",
    "text":      "#1e293b",
    "muted":     "#64748b",
    "input_bg":  "#f1f5f9",
    "btn":       "#2563eb",
    "btn_hover": "#1d4ed8",
}


class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather App")
        self.geometry("900x700")
        self.minsize(700, 550)
        self.resizable(True, True)

        self._unit = "metric"          # 'metric' or 'imperial'
        self._theme = "dark"
        self._colors = DARK.copy()
        self._icon_refs: list = []     # keep PhotoImage references alive

        self._build_ui()
        self.configure(bg=self._colors["bg"])
        self._auto_detect_city()

    # ── Build UI ─────────────────────────────────────────────────────────────
    def _build_ui(self):
        c = self._colors

        # ── Top bar ──
        self._topbar = tk.Frame(self, bg=c["panel"], height=60)
        self._topbar.pack(fill="x", side="top")
        self._topbar.pack_propagate(False)

        title_lbl = tk.Label(
            self._topbar, text="🌤 Weather App",
            font=("Segoe UI", 16, "bold"),
            bg=c["panel"], fg=c["text"],
        )
        title_lbl.pack(side="left", padx=20, pady=10)

        # Unit toggle
        self._unit_btn = tk.Button(
            self._topbar, text="Switch to °F",
            font=("Segoe UI", 9),
            bg=c["card"], fg=c["text"],
            relief="flat", cursor="hand2",
            command=self._toggle_unit,
            padx=10,
        )
        self._unit_btn.pack(side="right", padx=8, pady=12)

        # Theme toggle
        self._theme_btn = tk.Button(
            self._topbar, text="☀️ Light",
            font=("Segoe UI", 9),
            bg=c["card"], fg=c["text"],
            relief="flat", cursor="hand2",
            command=self._toggle_theme,
            padx=10,
        )
        self._theme_btn.pack(side="right", padx=4, pady=12)

        # ── Search bar ──
        self._searchbar = tk.Frame(self, bg=c["bg"], pady=12)
        self._searchbar.pack(fill="x", padx=20)

        self._city_var = tk.StringVar()
        self._city_entry = tk.Entry(
            self._searchbar,
            textvariable=self._city_var,
            font=("Segoe UI", 13),
            bg=c["input_bg"], fg=c["text"],
            insertbackground=c["text"],
            relief="flat", bd=0,
        )
        self._city_entry.pack(side="left", fill="x", expand=True,
                              ipady=10, padx=(0, 10))
        self._city_entry.bind("<Return>", lambda e: self._search())

        self._search_btn = tk.Button(
            self._searchbar, text="Get Weather",
            font=("Segoe UI", 11, "bold"),
            bg=c["btn"], fg="white",
            relief="flat", cursor="hand2",
            command=self._search, padx=16, pady=8,
        )
        self._search_btn.pack(side="right")

        # ── Error label ──
        self._error_var = tk.StringVar()
        self._error_lbl = tk.Label(
            self, textvariable=self._error_var,
            font=("Segoe UI", 10),
            bg=c["bg"], fg="#e94560",
        )
        self._error_lbl.pack(fill="x", padx=20)

        # ── Scrollable content ──
        self._canvas = tk.Canvas(self, bg=c["bg"], highlightthickness=0)
        self._scrollbar = ttk.Scrollbar(self, orient="vertical",
                                        command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._scrollbar.set)
        self._scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._content = tk.Frame(self._canvas, bg=c["bg"])
        self._canvas_window = self._canvas.create_window(
            (0, 0), window=self._content, anchor="nw"
        )

        self._content.bind("<Configure>", self._on_frame_configure)
        self._canvas.bind("<Configure>", self._on_canvas_configure)
        self._canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self._canvas.bind_all("<Button-4>", self._on_mousewheel)
        self._canvas.bind_all("<Button-5>", self._on_mousewheel)

        # ── Current weather panel ──
        self._current_panel = tk.Frame(self._content, bg=c["panel"],
                                       pady=20, padx=20)
        self._current_panel.pack(fill="x", padx=20, pady=(10, 6))

        # ── Hourly forecast panel ──
        self._hourly_frame = tk.Frame(self._content, bg=c["bg"])
        self._hourly_frame.pack(fill="x", padx=20, pady=6)

        # ── Daily forecast panel ──
        self._daily_frame = tk.Frame(self._content, bg=c["bg"])
        self._daily_frame.pack(fill="x", padx=20, pady=6)

    # ── Search ───────────────────────────────────────────────────────────────
    def _search(self):
        city = self._city_var.get().strip()
        if not city:
            self._show_error("Please enter a city name.")
            return
        self._show_error("")
        self._search_btn.configure(state="disabled", text="Loading...")
        threading.Thread(target=self._fetch, args=(city,), daemon=True).start()

    def _fetch(self, city: str):
        try:
            current_raw = get_current_weather(city, self._unit)
            forecast_raw = get_forecast(city, self._unit)
            current = parse_current(current_raw, self._unit)
            hourly = parse_hourly(forecast_raw, 6)
            daily = parse_daily(forecast_raw)
            self.after(0, self._render, current, hourly, daily)
        except (ValueError, ConnectionError) as exc:
            self.after(0, self._show_error, str(exc))
        finally:
            self.after(0, lambda: self._search_btn.configure(
                state="normal", text="Get Weather"
            ))

    # ── Render ───────────────────────────────────────────────────────────────
    def _render(self, current: dict, hourly: list, daily: list):
        self._render_current(current)
        self._render_hourly(hourly)
        self._render_daily(daily)

    def _render_current(self, c: dict):
        panel = self._current_panel
        for w in panel.winfo_children():
            w.destroy()
        self._icon_refs.clear()
        col = self._colors

        # Left: icon + temp
        left = tk.Frame(panel, bg=col["panel"])
        left.pack(side="left", padx=(0, 30))

        icon_img = load_icon(c["icon"], size=(80, 80))
        if icon_img:
            self._icon_refs.append(icon_img)
            tk.Label(left, image=icon_img, bg=col["panel"]).pack()

        tk.Label(
            left,
            text=format_temp(c["temp"], self._unit),
            font=("Segoe UI", 42, "bold"),
            bg=col["panel"], fg=col["text"],
        ).pack()

        tk.Label(
            left, text=c["description"],
            font=("Segoe UI", 13),
            bg=col["panel"], fg=col["muted"],
        ).pack()

        # Right: details
        right = tk.Frame(panel, bg=col["panel"])
        right.pack(side="left", fill="both", expand=True)

        tk.Label(
            right,
            text=f"{c['city']}, {c['country']}",
            font=("Segoe UI", 18, "bold"),
            bg=col["panel"], fg=col["text"],
        ).pack(anchor="w")

        details = [
            ("🌡 Feels like", format_temp(c["feels_like"], self._unit)),
            ("🌡 High / Low",
             f"{format_temp(c['temp_max'], self._unit)} / "
             f"{format_temp(c['temp_min'], self._unit)}"),
            ("💧 Humidity", f"{c['humidity']}%"),
            ("💨 Wind", format_wind(c["wind_speed"], self._unit)),
            ("👁 Visibility", f"{c['visibility']} km"),
            ("🌅 Sunrise", epoch_to_time(c["sunrise"])),
            ("🌇 Sunset", epoch_to_time(c["sunset"])),
        ]

        grid = tk.Frame(right, bg=col["panel"])
        grid.pack(anchor="w", pady=8)

        for i, (label, value) in enumerate(details):
            row, col_idx = divmod(i, 2)
            tk.Label(
                grid, text=f"{label}:",
                font=("Segoe UI", 9),
                bg=self._colors["panel"], fg=self._colors["muted"],
                width=16, anchor="w",
            ).grid(row=row, column=col_idx * 2, sticky="w", padx=(0, 4), pady=2)
            tk.Label(
                grid, text=value,
                font=("Segoe UI", 9, "bold"),
                bg=self._colors["panel"], fg=self._colors["text"],
                anchor="w",
            ).grid(row=row, column=col_idx * 2 + 1, sticky="w", padx=(0, 20), pady=2)

    def _render_hourly(self, hourly: list):
        frame = self._hourly_frame
        for w in frame.winfo_children():
            w.destroy()
        col = self._colors

        tk.Label(
            frame, text="Hourly Forecast",
            font=("Segoe UI", 12, "bold"),
            bg=col["bg"], fg=col["text"],
        ).pack(anchor="w", pady=(4, 6))

        cards = tk.Frame(frame, bg=col["bg"])
        cards.pack(fill="x")

        for item in hourly:
            card = tk.Frame(cards, bg=col["card"], padx=12, pady=8)
            card.pack(side="left", padx=6, pady=2)

            tk.Label(card, text=item["time"],
                     font=("Segoe UI", 9, "bold"),
                     bg=col["card"], fg=col["text"]).pack()

            icon_img = load_small_icon(item["icon"])
            if icon_img:
                self._icon_refs.append(icon_img)
                tk.Label(card, image=icon_img, bg=col["card"]).pack()

            tk.Label(card, text=format_temp(item["temp"], self._unit),
                     font=("Segoe UI", 11, "bold"),
                     bg=col["card"], fg=col["text"]).pack()

            tk.Label(card, text=item["description"],
                     font=("Segoe UI", 8),
                     bg=col["card"], fg=col["muted"],
                     wraplength=80).pack()

    def _render_daily(self, daily: list):
        frame = self._daily_frame
        for w in frame.winfo_children():
            w.destroy()
        col = self._colors

        tk.Label(
            frame, text="5-Day Forecast",
            font=("Segoe UI", 12, "bold"),
            bg=col["bg"], fg=col["text"],
        ).pack(anchor="w", pady=(4, 6))

        for item in daily:
            row = tk.Frame(frame, bg=col["card"], pady=8, padx=16)
            row.pack(fill="x", pady=3)

            tk.Label(row, text=item["day"],
                     font=("Segoe UI", 10, "bold"),
                     bg=col["card"], fg=col["text"],
                     width=12, anchor="w").pack(side="left")

            tk.Label(row, text=item["date"],
                     font=("Segoe UI", 9),
                     bg=col["card"], fg=col["muted"],
                     width=8, anchor="w").pack(side="left")

            icon_img = load_small_icon(item["icon"])
            if icon_img:
                self._icon_refs.append(icon_img)
                tk.Label(row, image=icon_img, bg=col["card"]).pack(side="left", padx=8)

            tk.Label(row, text=item["description"],
                     font=("Segoe UI", 9),
                     bg=col["card"], fg=col["muted"],
                     width=20, anchor="w").pack(side="left")

            tk.Label(row,
                     text=f"↑ {format_temp(item['temp_max'], self._unit)}  "
                          f"↓ {format_temp(item['temp_min'], self._unit)}",
                     font=("Segoe UI", 10, "bold"),
                     bg=col["card"], fg=col["text"]).pack(side="right", padx=8)

    # ── Helpers ──────────────────────────────────────────────────────────────
    def _show_error(self, msg: str):
        self._error_var.set(msg)

    def _toggle_unit(self):
        self._unit = "imperial" if self._unit == "metric" else "metric"
        label = "Switch to °C" if self._unit == "imperial" else "Switch to °F"
        self._unit_btn.configure(text=label)
        city = self._city_var.get().strip()
        if city:
            self._search()

    def _toggle_theme(self):
        self._theme = "light" if self._theme == "dark" else "dark"
        self._colors = LIGHT.copy() if self._theme == "light" else DARK.copy()
        self._theme_btn.configure(
            text="🌙 Dark" if self._theme == "light" else "☀️ Light"
        )
        self._apply_theme()

    def _apply_theme(self):
        """Apply current color scheme to all existing widgets."""
        c = self._colors
        self.configure(bg=c["bg"])

        def recolor(widget):
            cls = widget.winfo_class()
            try:
                if cls in ("Frame", "Canvas"):
                    widget.configure(bg=c["bg"] if widget == self._canvas or widget == self._content else c.get("panel", c["bg"]))
                elif cls == "Label":
                    # Detect which panel this label belongs to
                    parent_bg = widget.master.cget("bg") if widget.master else c["bg"]
                    widget.configure(bg=parent_bg)
            except Exception:
                pass
            for child in widget.winfo_children():
                recolor(child)

        # Recolor top-level containers explicitly
        self._topbar.configure(bg=c["panel"])
        self._searchbar.configure(bg=c["bg"])
        self._canvas.configure(bg=c["bg"])
        self._content.configure(bg=c["bg"])
        self._current_panel.configure(bg=c["panel"])
        self._hourly_frame.configure(bg=c["bg"])
        self._daily_frame.configure(bg=c["bg"])
        self._error_lbl.configure(bg=c["bg"])

        self._city_entry.configure(bg=c["input_bg"], fg=c["text"], insertbackground=c["text"])
        self._search_btn.configure(bg=c["btn"], fg="white")
        self._unit_btn.configure(bg=c["card"], fg=c["text"])
        self._theme_btn.configure(bg=c["card"], fg=c["text"])

        # Re-render weather if data is showing
        city = self._city_var.get().strip()
        if city:
            self._search()

    def _auto_detect_city(self):
        def _detect():
            city = detect_city_from_ip()
            if city:
                self.after(0, lambda: self._city_var.set(city))
                self.after(100, self._search)
        threading.Thread(target=_detect, daemon=True).start()

    def _on_frame_configure(self, event=None):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        self._canvas.itemconfig(self._canvas_window, width=event.width)

    def _on_mousewheel(self, event):
        if event.num == 4:
            self._canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self._canvas.yview_scroll(1, "units")
        else:
            self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
