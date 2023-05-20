from tkinter import *
from mttkinter import mtTkinter as tk
from tkinter import ttk
from ProcessInfo import ProcessInfo
import psutil
import threading
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Global variables for filters
selectedFilter = None
searchedText = None

def ProcessObtain():
    processInfo = ProcessInfo()
    processes = processInfo.getProcesses()
    return processes

def TableFill(totalMemory, processes):
    users = {}
    cont = 0
    try:
        for process in processes:
            memoryInfo = process.memory_info()
            physicalMemory = memoryInfo.rss
            cpuPercentage = (process.cpu_percent(interval=0) * 100) / psutil.cpu_count()
            memoryPercentage = physicalMemory / totalMemory * 100
            table.insert("", tk.END, values=(process.pid, process.name(), process.username(), process.status(), f"{cpuPercentage:.2f}%", f"{memoryPercentage:.2f}%"))

    except:
        pass

def updateTable():
    global totalMemory, selectedFilter, searchedText
    table.delete(*table.get_children())
    processes = ProcessObtain()
    if selectedFilter and searchedText:
        processes = [process for process in processes if filterProcess(process, selectedFilter, searchedText)]
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
    # Add y to data
    ys.append(psutil.cpu_percent() if ylabel == 'CPU' else psutil.virtual_memory().percent)

    # Limit y list to set number of items
    ys = ys[-x_len:]

    ax.clear()
    ax.plot(ys, label='{} usage (%)'.format(ylabel), color='b' if ylabel == 'CPU' else 'r')
    
    # Format plot
    ax.legend(loc='upper left')
    ax.set_title('{} usage over Time'.format(ylabel))
    ax.set_ylabel('Usage (%)')
    ax.set_ylim(0, 100)
    fig.canvas.draw()

def draw_plot(fig, ax, ys, canvas, ylabel):
    while True:
        animate(1, fig, ax, ys, ylabel)
        canvas.draw()
       

#Main window
root = Tk()
root.title("Resources Manager")
root.geometry("1200x820")

#Notebook
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

#Table of processes
table = ttk.Treeview(processesFrame)
table['columns'] = ('PID', 'NAME','USER', 'STATUS', 'CPU', 'MEMORY')
table.heading('PID', text='PID')
table.heading('NAME', text='NAME')
table.heading('USER', text='USER')
table.heading('STATUS', text='STATUS')
table.heading('CPU', text='CPU')
table.heading('MEMORY',text='MEMORY')
table.column('#0', width=0, stretch=tk.NO)
table.column("PID", width=50)
for column in table['columns']:
    table.column(column,anchor='center')
totalMemory = psutil.virtual_memory().total
scrollbar = ttk.Scrollbar(processesFrame, orient='vertical', command=table.yview)
table.configure(yscrollcommand=scrollbar.set)
processesFrame.grid_rowconfigure(1, weight=1)
processesFrame.grid_columnconfigure(0, weight=1)
table.grid(row=1,column=0,sticky='nsew')
scrollbar.grid(row=1,column=1,sticky='ns')


#Table of users
userTable = ttk.Treeview(usersFrame)
userTable["columns"] = ("User", "Processor", "Memory", "Swap")
userTable.heading("User", text="User")
userTable.heading("Processor", text="Processor")
userTable.heading("Memory", text="Memory")
userTable.heading("Swap", text="Swap")
userTable.column('#0', width=0, stretch=tk.NO)
for column in userTable['columns']:
    userTable.column(column,anchor='center')
userTable.grid(row=0, column=0, sticky="nsew")

#Container
container = tk.Frame(processesFrame)
container.grid(row=0, column=0, columnspan=3, sticky="NSEW")
container.grid_columnconfigure(0, weight=1)
container.grid_columnconfigure(1, weight=0)
container.grid_columnconfigure(2, weight=1)
container.grid_columnconfigure(3, weight=0)
container.grid_columnconfigure(4, weight=1)
#Label
label = tk.Label(container, text="Search: ")
label.grid(row=0, column=0, sticky="E")

#Dropdown
selectedOption = tk.StringVar()
dropdown = ttk.OptionMenu(container, selectedOption, 'Select','Name', 'User', 'Status')
dropdown.grid(row=0, column=1,sticky="W")

#Filter
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

# x variable for plotting
x_len = 200
ys_cpu = [0] * x_len
ys_mem = [0] * x_len

# Create canvas
canvas_cpu = FigureCanvasTkAgg(fig_cpu, master=performaceFrame)
canvas_mem = FigureCanvasTkAgg(fig_mem, master=performaceFrame)

canvas_cpu.get_tk_widget().grid(row=0, column=0)
canvas_mem.get_tk_widget().grid(row=1, column=0)


# Start separate thread for each plot
threading.Thread(target=draw_plot, args=(fig_cpu, ax_cpu, ys_cpu, canvas_cpu, 'CPU')).start()
threading.Thread(target=draw_plot, args=(fig_mem, ax_mem, ys_mem, canvas_mem, 'Memory')).start()


updateTable()
root.mainloop()