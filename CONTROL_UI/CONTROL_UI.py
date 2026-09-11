import queue
import random
from sys import int_info
import tkinter as tk
from tkinter import ttk
import serial
import os
import subprocess
from pathlib import Path
from datetime import datetime, timezone, timedelta
import pygame



ROOT :tk.Tk = tk.Tk();
ROOT.tk.call('tk', 'scaling', 2.5);
ROOT.title("Tkinter Tabs Example");
ROOT.attributes('-fullscreen', True);


STYLE :ttk.Style = ttk.Style();
QUEUE :queue.Queue;
NOTEBOOK : ttk.Notebook;
CAR_TAB : ttk.Frame;
MUSIC_TAB : ttk.Frame;
MUSIC_LABEL : ttk.Label;
WHEEL_CONTAINER :ttk.Frame;
WHEEL_LF : ttk.Button;
WHEEL_LB : ttk.Button;
WHEEL_RF : ttk.Button;
WHEEL_RB : ttk.Button;
AC_CONTAINER : ttk.Frame;
AC_ON_OFF_BTN : ttk.Button;
AC_TEMP_DOWN_BTN : ttk.Button;
AC_TEMP_UP_BTN : ttk.Button;
AC_STATE : bool = False;
DARK_MODE :bool = False;


STYLE.configure('TNotebook.Tab', font=('Arial', 12, 'bold'));
STYLE.configure('Wheel.TButton', font=('Arial', 12, 'bold'));
STYLE.configure('S.TButton', background='#4a4a4a', foreground='white', font=('Arial', 12, 'bold'));
STYLE.map('S.TButton', background=[('active', '#5a5a5a')]);
STYLE.configure('D.TButton', background='#ff6b6b', foreground='white', font=('Arial', 12, 'bold'));
STYLE.map('D.TButton', background=[('active', '#ff5252')]);
STYLE.configure('W.TButton', background='#fffacd', foreground='black', font=('Arial', 12, 'bold'));
STYLE.map('W.TButton', background=[('active', '#fff59d')]);



NO_HARDWARE = True;


PYTHON_FILE_DIRECTORY = Path(__file__).parent;
AUDIO_FILES_DIRECTORY = PYTHON_FILE_DIRECTORY / 'SONGS';


SONG_ARRAY :list[str] = [];
SONG_SOUND : pygame.mixer.Sound;
SONG_CHANNEL : pygame.mixer.Channel;
CURRENT_SONG_INDEX :int = 0;
SONG_IS_PLAYING :bool = False;



# ================== [TKINTER BS] ==================
#

def TOGGLE_DARKMODE():
    global DARK_MODE
    DARK_MODE = not DARK_MODE

    if DARK_MODE:
        ROOT.configure(bg='#1a1a1a')
        CAR_TAB.configure(style='Dark.TFrame')
        MUSIC_TAB.configure(style='Dark.TFrame')

        STYLE.configure('Dark.TFrame', background='#1a1a1a')
        STYLE.configure('Dark.TNotebook', background='#1a1a1a')
        STYLE.configure('Dark.TNotebook.Tab', background='#2d2d2d', foreground='white', font=('Arial', 12, 'bold'))
        STYLE.map('Dark.TNotebook.Tab', background=[('selected', '#3d3d3d')])

        MUSIC_LABEL.configure(style='Dark.TLabel', foreground='white')
        STYLE.configure('Dark.TLabel', background='#1a1a1a', foreground='white', font=('Arial', 16))

        WHEEL_LF.configure(style='Dark.TButton')
        WHEEL_RF.configure(style='Dark.TButton')
        WHEEL_LB.configure(style='Dark.TButton')
        WHEEL_RB.configure(style='Dark.TButton')
        STYLE.configure('Dark.TButton', background='#3d3d3d', foreground='white')
        STYLE.map('Dark.TButton', background=[('active', '#4d4d4d')])

        NOTEBOOK.configure(style='Dark.TNotebook')

    else:
        ROOT.configure(bg='#f0f0f0')
        CAR_TAB.configure(style='TFrame')
        MUSIC_TAB.configure(style='TFrame')

        MUSIC_LABEL.configure(style='TLabel', foreground='black')
        STYLE.configure('TLabel', background='#f0f0f0', foreground='black', font=('Arial', 16))

        WHEEL_LF.configure(style='TButton')
        WHEEL_RF.configure(style='TButton')
        WHEEL_LB.configure(style='TButton')
        WHEEL_RB.configure(style='TButton')
        STYLE.configure('TButton', background='#f0f0f0', foreground='black')

        NOTEBOOK.configure(style='TNotebook')
        STYLE.configure('TNotebook.Tab', font=('Arial', 12, 'bold'))
        STYLE.configure('TNotebook', background='#f0f0f0')




def INIT_AND_RUN_TK():
        global NOTEBOOK, CAR_TAB, MUSIC_TAB, MUSIC_LABEL, WHEEL_CONTAINER, WHEEL_LF, WHEEL_LB, WHEEL_RF, WHEEL_RB
        global AC_CONTAINER, AC_ON_OFF_BTN, AC_TEMP_DOWN_BTN, AC_TEMP_UP_BTN

        NOTEBOOK = ttk.Notebook(ROOT)
        NOTEBOOK.pack(expand=True, fill="both")

        # Tabs
        CAR_TAB = ttk.Frame(NOTEBOOK)
        MUSIC_TAB = ttk.Frame(NOTEBOOK)

        NOTEBOOK.add(CAR_TAB, text="CAR")
        NOTEBOOK.add(MUSIC_TAB, text="MUSIC")

        # Configure main tab grid split: Left half (col 0) & Right half (col 1)
        CAR_TAB.grid_columnconfigure(0, weight=1, uniform="half")
        CAR_TAB.grid_columnconfigure(1, weight=1, uniform="half")
        CAR_TAB.grid_rowconfigure(0, weight=1)
        CAR_TAB.grid_rowconfigure(1, weight=1)

        # --- Screen 1: Left Half (Wheel Control) ---
        WHEEL_CONTAINER = ttk.Frame(CAR_TAB)
        WHEEL_CONTAINER.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=20, pady=20)

        WHEEL_CONTAINER.grid_rowconfigure(0, weight=1)
        WHEEL_CONTAINER.grid_rowconfigure(1, weight=1)
        WHEEL_CONTAINER.grid_columnconfigure(0, weight=1)
        WHEEL_CONTAINER.grid_columnconfigure(1, weight=1)

        WHEEL_LF = ttk.Button(WHEEL_CONTAINER, text="LF", command=lambda: print("LF clicked"))
        WHEEL_LF.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        WHEEL_RF = ttk.Button(WHEEL_CONTAINER, text="RF", command=lambda: print("RF clicked"))
        WHEEL_RF.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        WHEEL_LB = ttk.Button(WHEEL_CONTAINER, text="LB", command=lambda: print("LB clicked"))
        WHEEL_LB.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        WHEEL_RB = ttk.Button(WHEEL_CONTAINER, text="RB", command=lambda: print("RB clicked"))
        WHEEL_RB.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        # --- Screen 2: Top Right (Empty Frame) ---
        EMPTY_CONTAINER = ttk.Frame(CAR_TAB)
        EMPTY_CONTAINER.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        # --- Screen 3: Bottom Right (AC Control) ---
        AC_CONTAINER = ttk.Frame(CAR_TAB)
        AC_CONTAINER.grid(row=1, column=1, sticky="nsew", padx=20, pady=20)

        AC_CONTAINER.grid_rowconfigure(0, weight=1)
        AC_CONTAINER.grid_rowconfigure(1, weight=1)
        AC_CONTAINER.grid_columnconfigure(0, weight=1)
        AC_CONTAINER.grid_columnconfigure(1, weight=1)

        AC_TEMP_DOWN_BTN = ttk.Button(AC_CONTAINER, text="◄ L", command=lambda: print("Temperature Decreased"))
        AC_TEMP_DOWN_BTN.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        AC_TEMP_UP_BTN = ttk.Button(AC_CONTAINER, text="H ►", command=lambda: print("Temperature Increased"))
        AC_TEMP_UP_BTN.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        AC_ON_OFF_BTN = ttk.Button(AC_CONTAINER, text="AC: OFF", command=TOGGLE_AC)
        AC_ON_OFF_BTN.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

        # --- MUSIC Tab Content ---
        MUSIC_LABEL = ttk.Label(MUSIC_TAB, text="Music Preferences", font=("Arial", 16))
        MUSIC_LABEL.pack(padx=20, pady=30)

        TOGGLE_DARKMODE()

        INIT__DISTANCE_RECIVER()

        ROOT.mainloop()

#
# ====================================================




def INIT_EVERYTHING():

        global SONG_ARRAY, ROOT;


        subprocess.run("clear", check=False);


        INIT__DISTANCE_RECIVER();


        INIT_MIXER_AND_SONG_LIST();


        INIT_AND_RUN_TK();




def TOGGLE_AC():

        global AC_STATE;


        AC_STATE = not AC_STATE;


        if AC_STATE:

                AC_ON_OFF_BTN.config(text="AC: ON");

                print("AC Turned ON");

        else:

                AC_ON_OFF_BTN.config(text="AC: OFF");

                print("AC Turned OFF");




def INIT__DISTANCE_RECIVER():

        global SERIAL;

        QUEUE = queue.Queue();

        if (not NO_HARDWARE) : SERIAL = serial.Serial('/dev/ttyUSB0', 9600, timeout=1);

        ROOT.after(100, UPDATE__DISTANCE_BUTTONS);




def GET__DISTANCE_SERIAL_LINE() -> str:

        global SERIAL;


        LINE = "";


        if (NO_HARDWARE):

                ALLOWED_DISTANCES = ['S', 'W', 'D'];


                for _ in range(4): LINE += random.choice(ALLOWED_DISTANCES);

        else:

                while SERIAL.in_waiting <= 0:

                        pass;

                LINE = SERIAL.readline().decode('utf-8').rstrip()


        return LINE;




def UPDATE__DISTANCE_BUTTONS():

        SERIAL_LINE = GET__DISTANCE_SERIAL_LINE();


        UPDATE_BUTTON_COLOR(WHEEL_LF, SERIAL_LINE[0]);
        UPDATE_BUTTON_COLOR(WHEEL_RF, SERIAL_LINE[3]);
        UPDATE_BUTTON_COLOR(WHEEL_LB, SERIAL_LINE[1]);
        UPDATE_BUTTON_COLOR(WHEEL_RB, SERIAL_LINE[2]);


        WHEEL_LF.config(text=SERIAL_LINE[0]);
        WHEEL_RF.config(text=SERIAL_LINE[3]);
        WHEEL_LB.config(text=SERIAL_LINE[1]);
        WHEEL_RB.config(text=SERIAL_LINE[2]);


        ROOT.after(10, UPDATE__DISTANCE_BUTTONS);




def UPDATE_BUTTON_COLOR(button, char):

        if   char == 'S' : button.configure(style='S.TButton');  # Dark gray

        elif char == 'W' : button.configure(style='W.TButton');  # Light yellow

        elif char == 'D' : button.configure(style='D.TButton');  # Light red




def INIT_MIXER_AND_SONG_LIST():

        global SONG_ARRAY, SONG_CHANNEL;


        pygame.mixer.init()


        SONG_CHANNEL = pygame.mixer.Channel(0);


        AUDIO_EXTENSIONS = ('.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a');


        SONG_ARRAY = [
                FILE for FILE in os.listdir(AUDIO_FILES_DIRECTORY)

                if FILE.lower().endswith(AUDIO_EXTENSIONS) and os.path.isfile(os.path.join(AUDIO_FILES_DIRECTORY, FILE))
        ];


        print("FOUND_SONGS : [");

        for FILE in SONG_ARRAY : print("    \"" + FILE + "\",");

        print("]");




def PLAY_SONG_INDEX(GIVEN_INDEX :int):

        global SONG_ARRAY, CURRENT_SONG_INDEX, SONG_IS_PLAYING;


        if (GIVEN_INDEX >= len(SONG_ARRAY) or GIVEN_INDEX < 0):

                LOG_ERROR("FAILED TO PLAY SONG : INVALID SONG INDEX");

                return;


        SONG_IS_PLAYING = True;


        CURRENT_SONG_INDEX = GIVEN_INDEX;


        CURRENT_SOUND = pygame.mixer.Sound(PYTHON_FILE_DIRECTORY / "SONGS" / SONG_ARRAY[GIVEN_INDEX]);


        SONG_CHANNEL.play(CURRENT_SOUND);




def PLAY_NEXT_SONG():


        if (CURRENT_SONG_INDEX >= len(SONG_ARRAY) - 1) :

                return;


        PLAY_SONG_INDEX(CURRENT_SONG_INDEX + 1);




def PLAY_PREV_SONG():


        if (CURRENT_SONG_INDEX == 0) :

                return;


        PLAY_SONG_INDEX(CURRENT_SONG_INDEX + 1);





def PAUSE_OR_UNPAUSE_SONG():

        global SONG_IS_PLAYING;


        if (SONG_IS_PLAYING) : SONG_CHANNEL.pause();

        else : SONG_CHANNEL.unpause();


        SONG_IS_PLAYING = not SONG_IS_PLAYING;




def LOG_ERROR(STRING) :


        CURRENT_TIME = datetime.now(timezone(timedelta(hours=8))).strftime("%H:%M:%S");


        print("\033[31m[ERROR] : [" + CURRENT_TIME + "] : " + STRING + "\033[0m");





INIT_EVERYTHING();
