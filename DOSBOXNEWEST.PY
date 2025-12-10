#!/usr/bin/env python3
import os
import tkinter as tk

LOADER_PATH = "C:/LOADER"
SEPARATOR = "109823949587483902982345]#;/]#;/;#"
os.makedirs(LOADER_PATH, exist_ok=True)

# ------------------ Create SYSLOADER files ------------------
# SHELL50-BIT.SYSLOADER (GUI Start Menu)
shell50_file = os.path.join(LOADER_PATH, "SHELL50-BIT.SYSLOADER")
if not os.path.isfile(shell50_file):
    shell50_code = [
        "import tkinter as tk",
        "from tkinter import messagebox",
        "def launch_shell():",
        "    messagebox.showinfo('Shell', 'Type shellcmd in emulator to start shell')",
        "root = tk.Tk()",
        "root.title('SHELL50-BIT START MENU')",
        "root.geometry('400x300')",
        "btn1 = tk.Button(root, text='Launch Shell', command=launch_shell)",
        "btn1.pack(pady=20)",
        "btn2 = tk.Button(root, text='Exit', command=root.destroy)",
        "btn2.pack(pady=20)",
        "root.mainloop()"
    ]
    with open(shell50_file, "w") as f:
        f.write(SEPARATOR.join(shell50_code))

# SHELLCOMMANDSTYPE.SYSLOADER (Commands)
shellcmd_file = os.path.join(LOADER_PATH, "SHELLCOMMANDSTYPE.SYSLOADER")
if not os.path.isfile(shellcmd_file):
    shellcmd_code = [
        "COMMANDS = ['LOAD','RUN','MEM','REG','CLR','HELP','EXIT']",
        "def execute_command(cmd, shell):",
        "    c = cmd.upper()",
        "    if c == 'HELP':",
        "        shell.print_line('Available commands: ' + ', '.join(COMMANDS))",
        "    elif c == 'CLR':",
        "        shell.clear()",
        "    elif c == 'EXIT':",
        "        shell.root.destroy()",
        "    else:",
        "        shell.print_line(f'Executing command: {cmd}')"
    ]
    with open(shellcmd_file, "w") as f:
        f.write(SEPARATOR.join(shellcmd_code))

# ------------------ Emulator with Canvas Shell ------------------
class CanvasShell:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SHELL50-BIT Emulator")
        self.root.geometry("1000x600")

        self.canvas = tk.Canvas(self.root, bg="blue")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.text_lines = []
        self.max_lines = 30
        self.line_height = 20
        self.font = ("Consolas", 12)
        self.input_buffer = ""
        self.cursor = "EMU> "

        self.commands_loaded = False
        self.commands_module = {}

        self.root.bind("<Key>", self.on_key)
        self.root.bind("<Return>", self.on_enter)

        self.show_start_message()

    def show_start_message(self):
        self.print_line("Welcome to SHELL50-BIT Emulator!")
        self.print_line("Type 'shell50' to open Start Menu or 'shellcmd' to launch shell commands.")
        self.print_prompt()

    def print_line(self, text=""):
        self.text_lines.append(text)
        if len(self.text_lines) > self.max_lines:
            self.text_lines = self.text_lines[-self.max_lines:]
        self.redraw()

    def print_prompt(self):
        self.redraw()

    def clear(self):
        self.text_lines = []
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        y = 5
        for line in self.text_lines:
            self.canvas.create_text(5, y, anchor="nw", text=line, fill="white", font=self.font)
            y += self.line_height
        # Draw input buffer
        self.canvas.create_text(5, y, anchor="nw", text=self.cursor + self.input_buffer, fill="white", font=self.font)

    def on_key(self, event):
        if event.keysym == "BackSpace":
            self.input_buffer = self.input_buffer[:-1]
        elif len(event.char) == 1:
            self.input_buffer += event.char
        self.redraw()

    def on_enter(self, event):
        cmd = self.input_buffer.strip()
        self.print_line(self.cursor + cmd)
        self.input_buffer = ""
        self.redraw()

        if cmd.lower() == "shell50":
            self.launch_start_menu()
        elif cmd.lower() == "shellcmd":
            self.load_commands()
        else:
            if self.commands_loaded:
                self.execute_loaded_command(cmd)
            else:
                self.print_line("Unknown command. Type 'shellcmd' to load commands.")
        self.print_prompt()

    # ------------------ Start Menu ------------------
    def launch_start_menu(self):
        shell50_path = os.path.join(LOADER_PATH, "SHELL50-BIT.SYSLOADER")
        if not os.path.isfile(shell50_path):
            self.print_line("SHELL50-BIT.SYSLOADER not found!")
            return
        try:
            with open(shell50_path, "r") as f:
                content = f.read()
            chunks = content.split(SEPARATOR)
            code = "\n".join(chunks)
            exec(code, {})
        except Exception as e:
            self.print_line(f"Error launching Start Menu: {e}")

    # ------------------ Load Commands ------------------
    def load_commands(self):
        shellcmd_path = os.path.join(LOADER_PATH, "SHELLCOMMANDSTYPE.SYSLOADER")
        if not os.path.isfile(shellcmd_path):
            self.print_line("SHELLCOMMANDSTYPE.SYSLOADER not found!")
            return
        try:
            with open(shellcmd_path, "r") as f:
                content = f.read()
            chunks = content.split(SEPARATOR)
            code = "\n".join(chunks)
            local_vars = {"shell": self}
            exec(code, {}, local_vars)
            self.commands_loaded = True
            self.commands_module = local_vars
            self.print_line("Command pack loaded. You can now type shell commands!")
        except Exception as e:
            self.print_line(f"Error loading commands: {e}")

    # ------------------ Execute loaded commands ------------------
    def execute_loaded_command(self, cmd):
        try:
            if "execute_command" in self.commands_module:
                func = self.commands_module["execute_command"]
                func(cmd, self)
            else:
                self.print_line("No execute_command function found.")
        except Exception as e:
            self.print_line(f"Error executing command: {e}")

    def start(self):
        self.root.mainloop()

# ------------------ Run Emulator ------------------
if __name__ == "__main__":
    shell = CanvasShell()
    shell.start()
