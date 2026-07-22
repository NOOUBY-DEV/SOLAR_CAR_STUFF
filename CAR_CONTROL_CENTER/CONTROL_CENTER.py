import tkinter as tk
from tkinter import ttk

# 1. Initialize the main application window
root = tk.Tk()
root.tk.call('tk', 'scaling', 2.5)
root.title("Tkinter Tabs Example")
root.attributes('-fullscreen', True)

# 2. Create the Notebook container
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both")

# 3. Create frames for each tab
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)

# 4. Add the frames to the notebook with custom titles
notebook.add(tab1, text="General Settings")
notebook.add(tab2, text="Advanced Options")

# 5. Add widgets inside Tab 1
label1 = ttk.Label(tab1, text="Welcome to the main dashboard.", font=("Arial", 12))
label1.pack(padx=20, pady=20)
button1 = ttk.Button(tab1, text="Save Changes")
button1.pack(pady=10)

# 6. Add widgets inside Tab 2
label2 = ttk.Label(tab2, text="Configure your database preferences here.")
label2.pack(padx=20, pady=20)
checkbox = ttk.Checkbutton(tab2, text="Enable Debug Mode")
checkbox.pack(pady=5)

# Start the main event loop
root.mainloop()
