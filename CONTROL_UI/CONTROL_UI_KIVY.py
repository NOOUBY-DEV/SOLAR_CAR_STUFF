#!/usr/bin/env python3
"""
CONTROL_UI ported to Kivy for Raspberry Pi 4
- Much smoother than tkinter
- Same features: CAR tab (distance buttons + AC), MUSIC tab, dark mode, pygame audio
"""

import os
import random
from pathlib import Path
from datetime import datetime, timezone, timedelta

import serial
import pygame

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.properties import BooleanProperty, StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.metrics import dp


# ================== CONFIG ==================
NO_HARDWARE = True                      # set False when real Arduino is connected
SERIAL_PORT = "/dev/ttyUSB0"
BAUD = 9600
UPDATE_INTERVAL = 0.05                 # 50 ms – much kinder than 10 ms
AUDIO_EXTENSIONS = (".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a")

PYTHON_FILE_DIRECTORY = Path(__file__).parent
AUDIO_FILES_DIRECTORY = PYTHON_FILE_DIRECTORY / "SONGS"


# ================== COLOURS ==================
COLORS = {
    "bg_dark":          (0.10, 0.10, 0.10, 1),
    "bg_light":         (0.94, 0.94, 0.94, 1),
    "panel_dark":       (0.18, 0.18, 0.18, 1),
    "panel_light":      (0.85, 0.85, 0.85, 1),
    "btn_normal_dark":  (0.24, 0.24, 0.24, 1),
    "btn_normal_light": (0.75, 0.75, 0.75, 1),
    "text_dark":        (1, 1, 1, 1),
    "text_light":       (0.1, 0.1, 0.1, 1),
    "S":                (0.29, 0.29, 0.29, 1),   # dark gray
    "W":                (1.00, 0.98, 0.80, 1),   # light yellow
    "D":                (1.00, 0.42, 0.42, 1),   # light red
    "accent":           (0.20, 0.60, 0.90, 1),
}


# ================== HELPERS ==================
def log_error(msg: str):
    now = datetime.now(timezone(timedelta(hours=8))).strftime("%H:%M:%S")
    print(f"\033[31m[ERROR] : [{now}] : {msg}\033[0m")


# ================== MAIN APP ==================
class ControlUI(App):
    dark_mode = BooleanProperty(True)
    ac_state = BooleanProperty(False)
    current_song_name = StringProperty("No Songs")
    song_is_playing = BooleanProperty(False)
    current_song_index = NumericProperty(0)

    # distance button texts
    lf_text = StringProperty("S")
    rf_text = StringProperty("S")
    lb_text = StringProperty("S")
    rb_text = StringProperty("S")

    def build(self):
        # Fullscreen on Pi
        Window.fullscreen = "auto"
        Window.show_cursor = False          # optional – nicer on touchscreen

        self.song_array = []
        self.song_channel = None
        self.serial = None

        self._init_audio()
        self._init_serial()

        root = self._build_ui()
        self._apply_theme()

        # start the distance update loop
        Clock.schedule_interval(self.update_distance_buttons, UPDATE_INTERVAL)

        return root

    # ------------------------------------------------------------------
    # Audio
    # ------------------------------------------------------------------
    def _init_audio(self):
        pygame.mixer.init()
        self.song_channel = pygame.mixer.Channel(0)

        if AUDIO_FILES_DIRECTORY.exists():
            self.song_array = [
                f for f in os.listdir(AUDIO_FILES_DIRECTORY)
                if f.lower().endswith(AUDIO_EXTENSIONS)
                and os.path.isfile(AUDIO_FILES_DIRECTORY / f)
            ]
            self.song_array.sort()

        print("FOUND_SONGS : [")
        for f in self.song_array:
            print(f'    "{f}",')
        print("]")

        if self.song_array:
            self.current_song_name = self._clean_name(self.song_array[0])

    def _clean_name(self, filename: str) -> str:
        name = filename
        for ext in AUDIO_EXTENSIONS:
            name = name.removesuffix(ext)
        return name

    def play_song_index(self, index: int):
        if index < 0 or index >= len(self.song_array):
            log_error("FAILED TO PLAY SONG : INVALID SONG INDEX")
            return

        self.current_song_index = index
        self.song_is_playing = True

        path = AUDIO_FILES_DIRECTORY / self.song_array[index]
        sound = pygame.mixer.Sound(str(path))
        self.song_channel.play(sound)

        self.current_song_name = self._clean_name(self.song_array[index])

    def play_next(self):
        if self.current_song_index < len(self.song_array) - 1:
            self.play_song_index(self.current_song_index + 1)

    def play_prev(self):
        if self.current_song_index > 0:
            self.play_song_index(self.current_song_index - 1)

    def toggle_play_pause(self):
        if self.song_is_playing:
            self.song_channel.pause()
        else:
            self.song_channel.unpause()
        self.song_is_playing = not self.song_is_playing

    # ------------------------------------------------------------------
    # Serial / Distance
    # ------------------------------------------------------------------
    def _init_serial(self):
        if not NO_HARDWARE:
            try:
                self.serial = serial.Serial(SERIAL_PORT, BAUD, timeout=1)
            except Exception as e:
                log_error(f"Serial open failed: {e}")
                self.serial = None

    def _get_distance_line(self) -> str:
        if NO_HARDWARE or self.serial is None:
            allowed = ["S", "W", "D"]
            return "".join(random.choice(allowed) for _ in range(4))

        try:
            if self.serial.in_waiting > 0:
                line = self.serial.readline().decode("utf-8", errors="ignore").rstrip()
                if len(line) >= 4:
                    return line[:4]
        except Exception as e:
            log_error(f"Serial read error: {e}")
        return "SSSS"

    def update_distance_buttons(self, dt):
        line = self._get_distance_line()
        # only update properties that actually changed
        if self.lf_text != line[0]:
            self.lf_text = line[0]
        if self.lb_text != line[1]:
            self.lb_text = line[1]
        if self.rb_text != line[2]:
            self.rb_text = line[2]
        if self.rf_text != line[3]:
            self.rf_text = line[3]

    # ------------------------------------------------------------------
    # UI Construction
    # ------------------------------------------------------------------
    def _build_ui(self):
        # We use a simple top bar + TabbedPanel
        root = BoxLayout(orientation="vertical")

        # ---- Top bar (dark mode + title) ----
        top = BoxLayout(size_hint_y=None, height=dp(50), padding=dp(6), spacing=dp(10))
        self.title_label = Label(
            text="CAR CONTROL",
            font_size="20sp",
            bold=True,
            size_hint_x=0.7,
        )
        top.add_widget(self.title_label)

        self.dark_btn = Button(
            text="DARK / LIGHT",
            size_hint_x=0.3,
            font_size="16sp",
            on_press=self.toggle_dark_mode,
        )
        top.add_widget(self.dark_btn)
        root.add_widget(top)

        # ---- Tabbed Panel ----
        self.tabs = TabbedPanel(do_default_tab=False, tab_pos="top_mid")
        self.tabs.background_color = (0, 0, 0, 0)   # transparent, we paint ourselves

        # ========== CAR TAB ==========
        car_tab = TabbedPanelItem(text="CAR")
        car_content = BoxLayout(orientation="horizontal", padding=dp(12), spacing=dp(12))

        # Left: Wheel 2x2
        wheel = GridLayout(cols=2, rows=2, spacing=dp(10), size_hint_x=0.5)
        self.btn_lf = self._make_dist_btn("lf_text")
        self.btn_rf = self._make_dist_btn("rf_text")
        self.btn_lb = self._make_dist_btn("lb_text")
        self.btn_rb = self._make_dist_btn("rb_text")
        wheel.add_widget(self.btn_lf)
        wheel.add_widget(self.btn_rf)
        wheel.add_widget(self.btn_lb)
        wheel.add_widget(self.btn_rb)
        car_content.add_widget(wheel)

        # Right side
        right = BoxLayout(orientation="vertical", size_hint_x=0.5, spacing=dp(12))

        # empty top-right panel (kept for layout parity)
        right.add_widget(Label(text="", size_hint_y=0.4))

        # AC controls
        self.btn_temp_down = Button(
            text="◄ L", font_size="22sp",
            on_press=lambda x: print("Temperature Decreased")
        )
        self.btn_temp_up = Button(
            text="H ►", font_size="22sp",
            on_press=lambda x: print("Temperature Increased")
        )
        self.btn_ac = Button(
            text="AC: OFF", font_size="20sp",
            on_press=self.toggle_ac
        )

        ac_layout = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=0.6)
        temp_row = BoxLayout(spacing=dp(10))
        temp_row.add_widget(self.btn_temp_down)
        temp_row.add_widget(self.btn_temp_up)
        ac_layout.add_widget(temp_row)
        ac_layout.add_widget(self.btn_ac)
        right.add_widget(ac_layout)

        car_content.add_widget(right)
        car_tab.add_widget(car_content)
        self.tabs.add_widget(car_tab)

        # ========== MUSIC TAB ==========
        music_tab = TabbedPanelItem(text="MUSIC")
        music_content = BoxLayout(orientation="horizontal", padding=dp(12), spacing=dp(12))

        # Left – song list (ScrollView + buttons)
        scroll = ScrollView(size_hint_x=0.5, do_scroll_x=False)
        song_box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(6))
        song_box.bind(minimum_height=song_box.setter("height"))

        self.song_buttons = []
        for idx, name in enumerate(self.song_array):
            btn = Button(
                text=name,
                size_hint_y=None,
                height=dp(56),
                font_size="16sp",
                on_press=lambda instance, i=idx: self.play_song_index(i),
            )
            song_box.add_widget(btn)
            self.song_buttons.append(btn)

        scroll.add_widget(song_box)
        self.song_list = scroll
        music_content.add_widget(scroll)

        # Right side
        music_right = BoxLayout(orientation="vertical", size_hint_x=0.5, spacing=dp(12))

        self.current_song_label = Label(
            text=self.current_song_name,
            font_size="22sp",
            bold=True,
            size_hint_y=0.4,
            halign="center",
            valign="middle",
        )
        self.current_song_label.bind(size=self.current_song_label.setter("text_size"))
        music_right.add_widget(self.current_song_label)

        # controls
        controls = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=0.6)
        nav = BoxLayout(spacing=dp(10))
        self.btn_prev = Button(text="◄ PREV", font_size="18sp", on_press=lambda x: self.play_prev())
        self.btn_next = Button(text="NEXT ►", font_size="18sp", on_press=lambda x: self.play_next())
        nav.add_widget(self.btn_prev)
        nav.add_widget(self.btn_next)
        controls.add_widget(nav)

        self.btn_play = Button(
            text="PLAY / STOP",
            font_size="20sp",
            on_press=lambda x: self.toggle_play_pause(),
        )
        controls.add_widget(self.btn_play)
        music_right.add_widget(controls)

        music_content.add_widget(music_right)
        music_tab.add_widget(music_content)
        self.tabs.add_widget(music_tab)

        root.add_widget(self.tabs)
        return root

    def _make_dist_btn(self, prop_name: str) -> Button:
        """Create a distance button that auto-updates colour from the property."""
        btn = Button(font_size="28sp", bold=True)
        # bind text
        self.bind(**{prop_name: btn.setter("text")})
        # initial colour
        self._set_btn_color(btn, getattr(self, prop_name))
        # keep colour in sync
        def on_text(instance, value):
            self._set_btn_color(btn, value)
        btn.bind(text=on_text)
        return btn

    def _set_btn_color(self, btn: Button, char: str):
        color = COLORS.get(char, COLORS["S"])
        btn.background_color = color
        # make text readable
        if char == "W":
            btn.color = (0.1, 0.1, 0.1, 1)
        else:
            btn.color = (1, 1, 1, 1)

    # ------------------------------------------------------------------
    # Theme / Dark mode
    # ------------------------------------------------------------------
    def toggle_dark_mode(self, *args):
        self.dark_mode = not self.dark_mode
        self._apply_theme()

    def _apply_theme(self):
        bg = COLORS["bg_dark"] if self.dark_mode else COLORS["bg_light"]
        panel = COLORS["panel_dark"] if self.dark_mode else COLORS["panel_light"]
        btn_c = COLORS["btn_normal_dark"] if self.dark_mode else COLORS["btn_normal_light"]
        text = COLORS["text_dark"] if self.dark_mode else COLORS["text_light"]

        Window.clearcolor = bg

        # top bar
        self.title_label.color = text
        self.dark_btn.background_color = btn_c
        self.dark_btn.color = text

        # AC + music controls
        for b in (self.btn_temp_down, self.btn_temp_up, self.btn_ac,
                  self.btn_prev, self.btn_next, self.btn_play):
            b.background_color = btn_c
            b.color = text

        self.current_song_label.color = text

        # song list buttons
        if hasattr(self, "song_buttons"):
            for b in self.song_buttons:
                b.background_color = btn_c
                b.color = text

        # distance buttons keep their own S/W/D colours

    def toggle_ac(self, *args):
        self.ac_state = not self.ac_state
        self.btn_ac.text = "AC: ON" if self.ac_state else "AC: OFF"
        print("AC Turned ON" if self.ac_state else "AC Turned OFF")

    # keep the current song label in sync
    def on_current_song_name(self, instance, value):
        if hasattr(self, "current_song_label"):
            self.current_song_label.text = value


# ================== ENTRY POINT ==================
if __name__ == "__main__":
    ControlUI().run()
