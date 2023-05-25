from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import *
from mttkinter import mtTkinter as tk
from tkinter import ttk
import psutil
import threading
import matplotlib
matplotlib.use("TkAgg")
import speedtest
from tkinter import messagebox
import sys
import time



class ProcessInfo:
    def __init__(self):
        self.processes = psutil.process_iter()

    def getProcesses(self):
        return list(self.processes)


# Global variables for filters
selectedFilter = None
searchedText = None


def on_closing():
    if messagebox.askokcancel("Exit", "Do you want to exit the program?"):
        root.destroy()
        sys.exit()
        

def get_network_speed():
    s = speedtest.Speedtest()
    s.get_best_server()
    #print(s.download()/(1024**2))
    return s.download() / (1024 ** 2)


def get_swap_usage():
    swap = psutil.swap_memory()
    return swap.used / swap.total


def ProcessObtain():
    processInfo = ProcessInfo()
    processes = processInfo.getProcesses()
    return processes


def usersTableFill(processes):
    try:
        users = {}
        usersMemory = {}
        usersProcessor = {}

        for process in processes:
            if process.username() not in users:
                users[process.username()] = len(users)
                usersMemory[process.username()] = 0
                usersProcessor[process.username()] = 0

            cpuPercentage = (process.cpu_percent() * 100) / psutil.cpu_count()
            usersMemory[process.username()] += process.memory_info().rss / psutil.virtual_memory().total
            usersProcessor[process.username()] += cpuPercentage

        for user, index in users.items():
            userTable.insert("", tk.END, values=(user, f"{usersProcessor[user] *.03 :.2f}%", f"{usersMemory[user]* 100:.2f}%"))

    except Exception:
        pass


def updateUserTable():
    processes = ProcessObtain()
    userTable.delete(*userTable.get_children())
    usersTableFill(processes)
    usersFrame.after(1250, updateUserTable)
    

def TableFill(totalMemory, processes):

    try:
        for process in processes:
            memoryInfo = process.memory_info()
            physicalMemory = memoryInfo.rss
            cpuPercentage = (process.cpu_percent(interval=0)
                             * 100) / psutil.cpu_count()
            memoryPercentage = physicalMemory / totalMemory * 100
            table.insert("", tk.END, values=(process.pid, process.name(), process.username(
            ), process.status(), f"{cpuPercentage * .03:.2f}%", f"{memoryPercentage:.2f}%"))

    except:
        pass


def updateTable():
    global totalMemory, selectedFilter, searchedText
    table.delete(*table.get_children())
    processes = ProcessObtain()
    if selectedFilter and searchedText:
        processes = [process for process in processes if filterProcess(
            process, selectedFilter, searchedText)]
    TableFill(totalMemory, processes)
    processesFrame.after(1250, updateTable)


def filterProcess(process, selectedColumn, searchedText):
    try:
        if selectedColumn == 'Name' and searchedText.lower() in process.name().lower():
            return True
        elif selectedColumn == 'User' and searchedText.lower() in process.username().lower():
            return True
        elif selectedColumn == 'Status' and searchedText.lower() in process.status().lower():
            return True
        else:
            return False
    except Exception:
        return False


def applyfilters():
    global selectedFilter, searchedText
    selectedFilter = selectedOption.get()
    searchedText = entry.get()
    updateTable()


def clearFilters():
    global selectedFilter, searchedText
    entry.delete(0, tk.END)
    selectedOption.set("Select")
    selectedFilter = None
    searchedText = None
    updateTable()


def animate(i, fig, ax, ys, ylabel):
    # Add new conditions for network and swap
    if ylabel == 'Network':
        ys.append(get_network_speed())
    elif ylabel == 'Swap':
        ys.append(get_swap_usage() * 100)
    else:
        ys.append(psutil.cpu_percent() if ylabel ==
                  'CPU' else psutil.virtual_memory().percent)

    # Limit y list to set number of items
    ys = ys[-x_len:]

    ax.clear()
    # Assign different colors to different plots
    if ylabel == 'CPU':
        color = 'b'
    elif ylabel == 'Memory':
        color = 'r'
    elif ylabel == 'Swap':
        color = 'g'
    else: # ylabel == 'Network':
        color = 'm'
    ax.plot(ys, label='{} usage (%)'.format(ylabel) if ylabel != 'Network' else 'Network usage (MBps)', color=color)

    # Format plot
    ax.legend(loc='upper left')
    ax.set_title('{} usage over Time'.format(ylabel))
    ax.set_ylabel('Usage (%)' if ylabel != 'Network' else 'Usage (MBps)')
    if ylabel != "Network":
        ax.set_ylim(0, 100)
    else:
        ax.set_ylim(0,250)
    fig.canvas.draw()


def draw_plot(fig, ax, ys, canvas, ylabel):
    while True:
        animate(1, fig, ax, ys, ylabel)
        canvas.draw()
        time.sleep(0.1)

try:
    # Main window
    root = Tk()
    root.title("Resources Manager")
    root.geometry("1200x820")

    # Notebook
    style = ttk.Style()
    style.configure("TNotebook.Tab", focuscolor="")
    notebook = ttk.Notebook(root, style="TNotebook")
    processesFrame = ttk.Frame(notebook)
    processesFrame.pack(fill=tk.BOTH, expand=True)
    performaceFrame = ttk.Frame(notebook)
    performaceFrame.pack(fill=tk.BOTH, expand=True)
    usersFrame = ttk.Frame(notebook)
    usersFrame.pack(fill=tk.BOTH, expand=True)
    notebook.add(processesFrame, text="Processes")
    notebook.add(performaceFrame, text="Performance")
    notebook.add(usersFrame, text="Users")
    notebook.pack(fill=tk.BOTH, expand=True)

    # Table of processes
    table = ttk.Treeview(processesFrame)
    table['columns'] = ('PID', 'NAME', 'USER', 'STATUS', 'CPU', 'MEMORY')
    table.heading('PID', text='PID')
    table.heading('NAME', text='NAME')
    table.heading('USER', text='USER')
    table.heading('STATUS', text='STATUS')
    table.heading('CPU', text='CPU')
    table.heading('MEMORY', text='MEMORY')
    table.column('#0', width=0, stretch=tk.NO)
    table.column("PID", width=50)
    for column in table['columns']:
        table.column(column, anchor='center')
    totalMemory = psutil.virtual_memory().total
    scrollbar = ttk.Scrollbar(
        processesFrame, orient='vertical', command=table.yview)
    table.configure(yscrollcommand=scrollbar.set)
    processesFrame.grid_rowconfigure(1, weight=1)
    processesFrame.grid_columnconfigure(0, weight=1)
    table.grid(row=1, column=0, sticky='nsew')
    scrollbar.grid(row=1, column=1, sticky='ns')


    # Table of users
    userTable = ttk.Treeview(usersFrame)
    userTable["columns"] = ("User", "Processor", "Memory")
    userTable.heading("User", text="User")
    userTable.heading("Processor", text="Processor")
    userTable.heading("Memory", text="Memory")
    userTable.column('#0', width=0, stretch=tk.NO)
    for column in userTable['columns']:
        userTable.column(column, anchor='center')
    userTable.grid(row=0, column=0, sticky="nsew")
    usersFrame.grid_rowconfigure(0, weight=1)
    usersFrame.grid_columnconfigure(0, weight=1)
  

    # Container
    container = tk.Frame(processesFrame)
    container.grid(row=0, column=0, columnspan=3, sticky="NSEW")
    container.grid_columnconfigure(0, weight=1)
    container.grid_columnconfigure(1, weight=0)
    container.grid_columnconfigure(2, weight=1)
    container.grid_columnconfigure(3, weight=0)
    container.grid_columnconfigure(4, weight=1)
    # Label
    label = tk.Label(container, text="Search: ")
    label.grid(row=0, column=0, sticky="E")

    # Dropdown
    selectedOption = tk.StringVar()
    dropdown = ttk.OptionMenu(container, selectedOption,
                            'Select', 'Name', 'User', 'Status')
    dropdown.grid(row=0, column=1, sticky="W")

    # Filter
    entry = tk.Entry(container, width=50)
    entry.grid(row=0, column=2, sticky="NSEW")
    buttonApply = tk.Button(container, text="Apply", command=applyfilters)
    buttonApply.grid(row=0, column=3, sticky="E")
    buttonClear = tk.Button(container, text="Clear filters", command=clearFilters)
    buttonClear.grid(row=0, column=4, sticky="W")

    # Performance Plots
    # Create figure for plotting
    fig_cpu = Figure(figsize=(5, 4), dpi=100)
    fig_mem = Figure(figsize=(5, 4), dpi=100)

    ax_cpu = fig_cpu.add_subplot(1, 1, 1)
    ax_mem = fig_mem.add_subplot(1, 1, 1)

    # Performance Plots
    x_len = 200
    ys_cpu = [0] * x_len
    ys_mem = [0] * x_len
    ys_swap = [0] * x_len
    ys_network = [0] * x_len

    fig_cpu = Figure(figsize=(5, 4), dpi=100)
    fig_mem = Figure(figsize=(5, 4), dpi=100)
    fig_swap = Figure(figsize=(5, 4), dpi=100)
    fig_network = Figure(figsize=(5, 4), dpi=100)

    ax_cpu = fig_cpu.add_subplot(1, 1, 1)
    ax_mem = fig_mem.add_subplot(1, 1, 1)
    ax_swap = fig_swap.add_subplot(1, 1, 1)
    ax_network = fig_network.add_subplot(1, 1, 1)

    canvas_cpu = FigureCanvasTkAgg(fig_cpu, master=performaceFrame)
    canvas_mem = FigureCanvasTkAgg(fig_mem, master=performaceFrame)
    canvas_swap = FigureCanvasTkAgg(fig_swap, master=performaceFrame)
    canvas_network = FigureCanvasTkAgg(fig_network, master=performaceFrame)

    canvas_cpu.get_tk_widget().grid(row=0, column=0, sticky="nsew", padx=(40,0))
    canvas_mem.get_tk_widget().grid(row=1, column=0, sticky="nsew", padx=(40,0))
    canvas_swap.get_tk_widget().grid(row=0, column=1, sticky="nsew", padx=(110,0))
    canvas_network.get_tk_widget().grid(row=1, column=1, sticky="nsew", padx=(110,0))

    threading.Thread(target=draw_plot, args=(
        fig_cpu, ax_cpu, ys_cpu, canvas_cpu, 'CPU')).start()
    threading.Thread(target=draw_plot, args=(
        fig_mem, ax_mem, ys_mem, canvas_mem, 'Memory')).start()
    threading.Thread(target=draw_plot, args=(
        fig_swap, ax_swap, ys_swap, canvas_swap, 'Swap')).start()
    threading.Thread(target=draw_plot, args=(fig_network, ax_network,
                    ys_network, canvas_network, 'Network')).start()


    updateTable()
    updateUserTable()
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
except Exception:
    sys.exit()