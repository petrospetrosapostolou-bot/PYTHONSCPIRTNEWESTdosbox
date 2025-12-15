import os
import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog

# ---------- FILE SYSTEM ----------
LOADER = "C:/LOADER"
DISKS = os.path.join(LOADER, "DISKS")
os.makedirs(DISKS, exist_ok=True)

# ---------- CPU ----------
class CPU:
    def __init__(self):
        self.registers = {f"R{i}":0 for i in range(8)}
        self.registers.update({"AX":0,"BX":0,"CX":0,"DX":0})
        self.max_val = 2**50-1
        self.flags = {"Z":0,"C":0,"O":0}
        self.stack = []

    def dump_registers(self):
        return " | ".join(f"{k}={v}" for k,v in self.registers.items())

    def execute(self,instr,shell):
        parts = instr.strip().split()
        if not parts: return
        cmd = parts[0].upper()
        try:
            if cmd=="MOV" and len(parts)==3:
                reg,val=parts[1].upper(),parts[2]
                if reg in self.registers:
                    self.registers[reg]=int(val)&self.max_val
                else: shell.print_error("Invalid register")
            elif cmd=="ADD" and len(parts)==3:
                r1,r2=parts[1].upper(),parts[2].upper()
                self.registers[r1]+=self.registers[r2]
                self.flags["C"]=int(self.registers[r1]>self.max_val)
                self.registers[r1]=min(self.registers[r1],self.max_val)
            elif cmd=="SUB" and len(parts)==3:
                r1,r2=parts[1].upper(),parts[2].upper()
                self.registers[r1]-=self.registers[r2]
                if self.registers[r1]<0: self.registers[r1]=0
            elif cmd=="MUL" and len(parts)==3:
                r1,r2=parts[1].upper(),parts[2].upper()
                self.registers[r1]*=self.registers[r2]
                self.flags["C"]=int(self.registers[r1]>self.max_val)
                self.registers[r1]=min(self.registers[r1],self.max_val)
            elif cmd=="DIV" and len(parts)==3:
                r1,r2=parts[1].upper(),parts[2].upper()
                if self.registers[r2]==0:
                    shell.print_error("Division by zero")
                else: self.registers[r1]//=self.registers[r2]
            elif cmd in ("INC","DEC") and len(parts)==2:
                reg=parts[1].upper()
                if cmd=="INC": self.registers[reg]+=1
                else: 
                    self.registers[reg]-=1
                    if self.registers[reg]<0: self.registers[reg]=0
            elif cmd=="MOD" and len(parts)==3:
                r1,r2=parts[1].upper(),parts[2].upper()
                if self.registers[r2]==0: shell.print_error("Modulo by zero")
                else: self.registers[r1]%=self.registers[r2]
            elif cmd=="AND" and len(parts)==3:
                r1,r2=parts[1].upper(),parts[2].upper()
                self.registers[r1]&=self.registers[r2]
            elif cmd=="OR" and len(parts)==3:
                r1,r2=parts[1].upper(),parts[2].upper()
                self.registers[r1]|=self.registers[r2]
            elif cmd=="XOR" and len(parts)==3:
                r1,r2=parts[1].upper(),parts[2].upper()
                self.registers[r1]^=self.registers[r2]
            elif cmd=="NOT" and len(parts)==2:
                reg=parts[1].upper()
                self.registers[reg]=~self.registers[reg]&self.max_val
            elif cmd=="PUSH" and len(parts)==2:
                reg=parts[1].upper()
                self.stack.append(self.registers[reg])
            elif cmd=="POP" and len(parts)==2:
                reg=parts[1].upper()
                if self.stack: self.registers[reg]=self.stack.pop()
                else: shell.print_error("Stack empty")
            elif cmd=="CMP" and len(parts)==3:
                r1,r2=parts[1].upper(),parts[2].upper()
                self.flags["Z"]=int(self.registers[r1]==self.registers[r2])
            elif cmd in ("JMP","JE","JNE"):
                shell.print_info(f"{cmd} not implemented yet")
            elif cmd=="PRN" and len(parts)==2:
                reg=parts[1].upper()
                shell.print_info(f"{reg}={self.registers[reg]}")
            elif cmd=="DUMP":
                shell.print_info(self.dump_registers())
            else:
                shell.print_error("Unknown CPU command")
        except Exception as e:
            shell.print_error(str(e))

# ---------- RAM ----------
class RAM:
    def __init__(self,size=4096):
        self.size=size
        self.mem=[0]*size

    def load(self,addr,shell):
        try:
            addr=int(addr)
            if 0<=addr<self.size: return self.mem[addr]
            shell.print_error("Address out of range")
        except: shell.print_error("Invalid address")
        return None

    def store(self,addr,val,shell):
        try:
            addr=int(addr)
            val=int(val)
            if 0<=addr<self.size: self.mem[addr]=val&0xFF
            else: shell.print_error("Address out of range")
        except: shell.print_error("Invalid address/value")

# ---------- EMULATOR ----------
class Emulator:
    def __init__(self):
        self.root=tk.Tk()
        self.root.title("SHELL50-BIT Combined")
        self.root.geometry("1000x600")

        self.cpu=CPU()
        self.ram=RAM()

        # Tabs
        self.tabs=ttk.Notebook(self.root)
        self.tabs.pack(fill="both",expand=True)

        # Shell Tab
        self.shell_tab=tk.Frame(self.tabs)
        self.tabs.add(self.shell_tab,text="SHELL")

        # Scrollable output
        self.output=scrolledtext.ScrolledText(self.shell_tab,bg="black",fg="white",font=("Consolas",12),state="disabled")
        self.output.pack(fill="both",expand=True)

        # Input Entry
        self.input_entry=tk.Entry(self.shell_tab,bg="black",fg="white",font=("Consolas",12),insertbackground="white")
        self.input_entry.pack(fill="x")
        self.input_entry.bind("<Return>",self.enter_command)
        self.input_entry.focus()

        # Status bar
        self.status=tk.Label(self.root,text="CPU: -- | RAM Used: 0/4096",anchor="w")
        self.status.pack(fill="x")

        # Disk tab
        self.disk_tab_created=False
        self.prompt="EMU> "

        # Welcome messages
        self.print_info("SHELL50-BIT READY (Combined)")
        self.print_info("Type DISK to create Disk Tab")
        self.print_info("CPU: MOV ADD SUB MUL DIV INC DEC MOD AND OR XOR NOT PUSH POP PRN DUMP")
        self.print_info("RAM: LOAD addr STORE addr val")
        self.update_status()

    # --- Output methods ---
    def print(self,text,color=None):
        self.output.configure(state="normal")
        if color: self.output.insert("end",text+"\n",color)
        else: self.output.insert("end",text+"\n")
        self.output.see("end")
        self.output.configure(state="disabled")

    def print_error(self,text):
        self.print(text,"error")
        self.output.tag_config("error",foreground="red")

    def print_info(self,text):
        self.print(text,"info")
        self.output.tag_config("info",foreground="green")

    def update_status(self):
        used=sum(1 for b in self.ram.mem if b!=0)
        self.status.config(text=f"CPU: -- | RAM Used: {used}/{self.ram.size}")

    # --- Command handler ---
    def enter_command(self,event):
        cmd=self.input_entry.get().strip()
        self.input_entry.delete(0,"end")
        self.print(f"{self.prompt}{cmd}")

        parts=cmd.upper().split()
        if not parts: return "break"

        if parts[0]=="DISK":
            self.create_disk_tab()
        elif parts[0] in ("MOV","ADD","SUB","MUL","DIV","INC","DEC","MOD",
                          "AND","OR","XOR","NOT","PUSH","POP","PRN","DUMP","CMP","JMP","JE","JNE"):
            self.cpu.execute(cmd,self)
        elif parts[0]=="LOAD" and len(parts)==2:
            val=self.ram.load(parts[1],self)
            if val is not None: self.print_info(f"RAM[{parts[1]}]={val}")
        elif parts[0]=="STORE" and len(parts)==3:
            self.ram.store(parts[1],parts[2],self)
            self.print_info(f"Stored {parts[2]} at RAM[{parts[1]}]")
        elif parts[0]=="HELP":
            self.print_info("CPU: MOV ADD SUB MUL DIV INC DEC MOD AND OR XOR NOT PUSH POP PRN DUMP")
            self.print_info("RAM: LOAD addr, STORE addr val")
            self.print_info("DISK: DISK")
        else:
            self.print_error("UNKNOWN COMMAND")

        self.update_status()
        return "break"

    # --- Disk Tab ---
    def create_disk_tab(self):
        if self.disk_tab_created:
            self.tabs.select(self.disk_tab)
            self.print_info("DISK TAB ALREADY CREATED")
            return
        self.disk_tab_created=True
        self.disk_tab=tk.Frame(self.tabs)
        self.tabs.add(self.disk_tab,text="DISK")
        self.tabs.select(self.disk_tab)
        tk.Label(self.disk_tab,text="Disk Tab coming soon").pack()

    # --- Run ---
    def start(self):
        self.root.mainloop()

# ---------- RUN ----------
if __name__=="__main__":
    Emulator().start()
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 