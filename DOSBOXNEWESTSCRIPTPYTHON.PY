import os
import tkinter as tk
from tkinter import ttk

# ---------- FILE SYSTEM ----------
LOADER = "C:/LOADER"
DISKS = os.path.join(LOADER, "DISKS")
os.makedirs(DISKS, exist_ok=True)

# ---------- CPU & RAM SIMULATION ----------
class CPU:
    def __init__(self):
        self.registers = {f"R{i}": 0 for i in range(8)}  # 8 registers
        self.max_val = 2**50 - 1  # 50-bit max

    def execute(self, instr, shell):
        parts = instr.strip().split()
        if not parts:
            return

        cmd = parts[0].upper()
        if cmd == "MOV" and len(parts) == 3:
            reg, val = parts[1].upper(), parts[2]
            if reg in self.registers:
                try:
                    v = int(val)
                    if 0 <= v <= self.max_val:
                        self.registers[reg] = v
                    else:
                        shell.print(f"ERROR: Value out of 50-bit range")
                except:
                    shell.print(f"ERROR: Invalid value")
            else:
                shell.print(f"ERROR: Invalid register")
        elif cmd in ("ADD","SUB") and len(parts) == 3:
            r1, r2 = parts[1].upper(), parts[2].upper()
            if r1 in self.registers and r2 in self.registers:
                if cmd == "ADD":
                    self.registers[r1] += self.registers[r2]
                    if self.registers[r1] > self.max_val:
                        self.registers[r1] = self.max_val
                else:
                    self.registers[r1] -= self.registers[r2]
                    if self.registers[r1] < 0:
                        self.registers[r1] = 0
            else:
                shell.print("ERROR: Invalid register")
        elif cmd == "PRN" and len(parts) == 2:
            reg = parts[1].upper()
            if reg in self.registers:
                shell.print(f"{reg} = {self.registers[reg]}")
            else:
                shell.print("ERROR: Invalid register")
        else:
            shell.print("ERROR: Invalid CPU command")

class RAM:
    def __init__(self):
        self.size = 1024
        self.mem = [0]*self.size

    def load(self, addr, shell):
        try:
            addr = int(addr)
            if 0 <= addr < self.size:
                return self.mem[addr]
            else:
                shell.print("ERROR: Address out of range")
                return None
        except:
            shell.print("ERROR: Invalid address")
            return None

    def store(self, addr, val, shell):
        try:
            addr = int(addr)
            val = int(val)
            if 0 <= addr < self.size:
                self.mem[addr] = val & 0xFF
            else:
                shell.print("ERROR: Address out of range")
        except:
            shell.print("ERROR: Invalid address or value")

# ---------- EMULATOR ----------
class Emulator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SHELL50-BIT Emulator")
        self.root.geometry("1000x600")

        # Tabs
        self.tabs = ttk.Notebook(self.root)
        self.tabs.pack(fill="both", expand=True)

        # SHELL TAB
        self.shell_tab = tk.Frame(self.tabs)
        self.tabs.add(self.shell_tab, text="SHELL")

        self.canvas = tk.Canvas(self.shell_tab, bg="blue")
        self.canvas.pack(fill="both", expand=True)

        self.lines = []
        self.input_buf = ""
        self.prompt = "EMU> "
        self.font = ("Consolas", 12)

        # DISK tab state
        self.disk_tab_created = False

        # CPU & RAM
        self.cpu = CPU()
        self.ram = RAM()

        self.root.bind("<Key>", self.key)
        self.root.bind("<Return>", self.enter)

        self.print("SHELL50-BIT READY")
        self.print("Type DISK to create Disk Maker tab")
        self.print("CPU commands: MOV, ADD, SUB, PRN")
        self.print("RAM commands: LOAD, STORE, DUMP")

    # ---------- SHELL ----------
    def print(self, text):
        self.lines.append(text)
        self.lines = self.lines[-30:]
        self.redraw()

    def redraw(self):
        self.canvas.delete("all")
        y = 5
        for l in self.lines:
            self.canvas.create_text(5, y, anchor="nw", text=l, fill="white", font=self.font)
            y += 18
        self.canvas.create_text(5, y, anchor="nw", text=self.prompt + self.input_buf, fill="white", font=self.font)

    def key(self, e):
        if e.keysym == "BackSpace":
            self.input_buf = self.input_buf[:-1]
        elif len(e.char) == 1:
            self.input_buf += e.char
        self.redraw()

    def enter(self, e):
        cmd = self.input_buf.strip()
        self.print(self.prompt + cmd)
        self.input_buf = ""

        # ---- DISK TAB CREATOR ----
        if cmd.upper() == "DISK":
            self.create_disk_tab()
        # ---- CPU commands ----
        elif cmd.upper().split()[0] in ("MOV","ADD","SUB","PRN"):
            self.cpu.execute(cmd, self)
        # ---- RAM commands ----
        elif cmd.upper().split()[0] == "LOAD":
            parts = cmd.split()
            if len(parts) == 2:
                val = self.ram.load(parts[1], self)
                if val is not None:
                    self.print(f"RAM[{parts[1]}] = {val}")
            else:
                self.print("ERROR: LOAD addr")
        elif cmd.upper().split()[0] == "STORE":
            parts = cmd.split()
            if len(parts) == 3:
                self.ram.store(parts[1], parts[2], self)
                self.print(f"Stored {parts[2]} at RAM[{parts[1]}]")
            else:
                self.print("ERROR: STORE addr value")
        elif cmd.upper() == "DUMP":
            self.print("RAM DUMP:")
            for i in range(0, 1024, 16):
                line = " ".join(f"{b:02X}" for b in self.ram.mem[i:i+16])
                self.print(f"{i:03}: {line}")
        # ---- HELP ----
        elif cmd.upper() == "HELP":
            self.print("Commands: DISK, MOV, ADD, SUB, PRN, LOAD, STORE, DUMP, HELP")
        else:
            self.print("UNKNOWN COMMAND")

        self.redraw()

    # ---------- DISK TAB CREATOR ----------
    def create_disk_tab(self):
        if self.disk_tab_created:
            self.tabs.select(self.disk_tab)
            self.print("DISK TAB ALREADY CREATED")
            return

        self.disk_tab_created = True
        self.disk_tab = tk.Frame(self.tabs)
        self.tabs.add(self.disk_tab, text="DISK")
        self.tabs.select(self.disk_tab)

        # ---------- IMG Maker ----------
        tk.Label(self.disk_tab, text="IMG Maker (1 MB max)").pack(anchor="w", pady=(5,0))
        tk.Label(self.disk_tab, text="File Path:").pack(anchor="w")
        self.img_path = tk.Entry(self.disk_tab)
        self.img_path.pack(fill="x", padx=5)

        self.img_progress = ttk.Progressbar(self.disk_tab, length=300)
        self.img_progress.pack(pady=5)

        tk.Button(self.disk_tab, text="Create IMG", command=lambda: self.make_disk("IMG")).pack(pady=(0,10))

        # ---------- FLP Maker ----------
        tk.Label(self.disk_tab, text="FLP Maker (1 KB max)").pack(anchor="w", pady=(5,0))
        tk.Label(self.disk_tab, text="File Path:").pack(anchor="w")
        self.flp_path = tk.Entry(self.disk_tab)
        self.flp_path.pack(fill="x", padx=5)

        self.flp_progress = ttk.Progressbar(self.disk_tab, length=300)
        self.flp_progress.pack(pady=5)

        tk.Button(self.disk_tab, text="Create FLP", command=lambda: self.make_disk("FLP")).pack(pady=(0,10))

        self.print("DISK TAB CREATED")

    # ---------- CREATE DISK FUNCTION ----------
    def make_disk(self, dtype):
        if dtype == "IMG":
            src = self.img_path.get()
            limit = 1024*1024
            bar = self.img_progress
            ext = ".img"
        else:
            src = self.flp_path.get()
            limit = 1024
            bar = self.flp_progress
            ext = ".flp"

        if not os.path.isfile(src):
            self.print(f"{dtype} ERROR: File not found")
            return

        out_file = os.path.join(DISKS, os.path.basename(src) + ext)
        written = 0
        bar["value"] = 0

        with open(src, "rb") as f, open(out_file, "wb") as o:
            while written < limit:
                chunk = f.read(64)
                if not chunk:
                    break
                o.write(chunk)
                written += len(chunk)
                bar["value"] = (written / limit) * 100
                self.root.update()

        self.print(f"{dtype} CREATED: {out_file}")

    def start(self):
        self.root.mainloop()

# ---------- RUN ----------
if __name__ == "__main__":
    Emulator().start()
