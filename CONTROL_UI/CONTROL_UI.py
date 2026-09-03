import tkinter as tk
from tkinter import ttk

ROOT = tk.Tk()
ROOT.tk.call('tk', 'scaling', 2.5)
ROOT.title("Tkinter Tabs Example")
ROOT.attributes('-fullscreen', True)

# Configure style for consistent look
STYLE = ttk.Style()
STYLE.configure('TNotebook.Tab', font=('Arial', 12, 'bold'))

# Dark mode state
DARK_MODE = False

def toggle_dark_mode():
    global DARK_MODE
    DARK_MODE = not DARK_MODE

    if DARK_MODE:
        # Set dark background for root and all frames
        ROOT.configure(bg='#1a1a1a')
        CAR_TAB.configure(style='Dark.TFrame')
        MUSIC_TAB.configure(style='Dark.TFrame')

        # Configure dark styles
        STYLE.configure('Dark.TFrame', background='#1a1a1a')
        STYLE.configure('Dark.TNotebook', background='#1a1a1a')
        STYLE.configure('Dark.TNotebook.Tab', background='#2d2d2d', foreground='white', font=('Arial', 12, 'bold'))
        STYLE.map('Dark.TNotebook.Tab', background=[('selected', '#3d3d3d')])

        # Update labels
        MUSIC_LABEL.configure(style='Dark.TLabel', foreground='white')
        STYLE.configure('Dark.TLabel', background='#1a1a1a', foreground='white', font=('Arial', 16))

        # Update buttons
        WHEEL_LF.configure(style='Dark.TButton')
        WHEEL_RF.configure(style='Dark.TButton')
        WHEEL_LB.configure(style='Dark.TButton')
        WHEEL_RB.configure(style='Dark.TButton')
        STYLE.configure('Dark.TButton', background='#3d3d3d', foreground='white')
        STYLE.map('Dark.TButton', background=[('active', '#4d4d4d')])

        # Update notebook
        NOTEBOOK.configure(style='Dark.TNotebook')

    else:
        # Reset to light mode
        ROOT.configure(bg='#f0f0f0')
        CAR_TAB.configure(style='TFrame')
        MUSIC_TAB.configure(style='TFrame')

        # Reset labels
        MUSIC_LABEL.configure(style='TLabel', foreground='black')
        STYLE.configure('TLabel', background='#f0f0f0', foreground='black', font=('Arial', 16))

        # Reset buttons
        WHEEL_LF.configure(style='TButton')
        WHEEL_RF.configure(style='TButton')
        WHEEL_LB.configure(style='TButton')
        WHEEL_RB.configure(style='TButton')
        STYLE.configure('TButton', background='#f0f0f0', foreground='black')

        # Reset notebook
        NOTEBOOK.configure(style='TNotebook')
        STYLE.configure('TNotebook.Tab', font=('Arial', 12, 'bold'))
        STYLE.configure('TNotebook', background='#f0f0f0')

# Create the Notebook container
NOTEBOOK = ttk.Notebook(ROOT)
NOTEBOOK.pack(expand=True, fill="both")

# Create frames for each tab
CAR_TAB = ttk.Frame(NOTEBOOK)
MUSIC_TAB = ttk.Frame(NOTEBOOK)

# Add the frames to the notebook with custom titles
NOTEBOOK.add(CAR_TAB, text="CAR")
NOTEBOOK.add(MUSIC_TAB, text="MUSIC")

# Create a container frame for the wheel buttons
WHEEL_CONTAINER = ttk.Frame(CAR_TAB)
WHEEL_CONTAINER.pack(expand=True, fill="both", padx=50, pady=50)

# Configure grid for the wheel buttons (2x2 grid)
WHEEL_CONTAINER.grid_rowconfigure(0, weight=1)
WHEEL_CONTAINER.grid_rowconfigure(1, weight=1)
WHEEL_CONTAINER.grid_columnconfigure(0, weight=1)
WHEEL_CONTAINER.grid_columnconfigure(1, weight=1)

# Create wheel buttons in 2x2 grid - tall instead of wide
WHEEL_LF = ttk.Button(WHEEL_CONTAINER, text="LF", command=lambda: print("LF clicked"))
WHEEL_LF.grid(row=0, column=0, padx=20, pady=20, ipadx=20, ipady=40)

WHEEL_RF = ttk.Button(WHEEL_CONTAINER, text="RF", command=lambda: print("RF clicked"))
WHEEL_RF.grid(row=0, column=1, padx=20, pady=20, ipadx=20, ipady=40)

WHEEL_LB = ttk.Button(WHEEL_CONTAINER, text="LB", command=lambda: print("LB clicked"))
WHEEL_LB.grid(row=1, column=0, padx=20, pady=20, ipadx=20, ipady=40)

WHEEL_RB = ttk.Button(WHEEL_CONTAINER, text="RB", command=lambda: print("RB clicked"))
WHEEL_RB.grid(row=1, column=1, padx=20, pady=20, ipadx=20, ipady=40)

# Add widgets inside MUSIC Tab
MUSIC_LABEL = ttk.Label(MUSIC_TAB, text="Music Preferences", font=("Arial", 16))
MUSIC_LABEL.pack(padx=20, pady=30)

# Call dark mode function at the bottom
toggle_dark_mode()

# Start the main event loop
ROOT.mainloop()
