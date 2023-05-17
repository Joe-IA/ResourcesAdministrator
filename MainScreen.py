from tkinter import *
import tkinter as tk
from tkinter import ttk
from ProcessInfo import ProcessInfo
import psutil


def ProcessObtain():
    processInfo = ProcessInfo()
    processes = processInfo.getProcesses()
    return processes

def TableFill(totalMemory, processes):
    try:
        for process in processes:
            memoryInfo = process.memory_info()
            physicalMemory = memoryInfo.rss
            cpuPercentage = process.cpu_percent() * 100 / psutil.cpu_count()
            memoryPercentage = physicalMemory / totalMemory * 100
            table.insert("", tk.END, values=(process.pid, process.name(), process.username(), process.nice(), process.status(), f"{cpuPercentage:.2f}%", f"{memoryPercentage:.2f}%"))
    except:
        pass

def updateTable(processes):
    global totalMemory
    table.delete(*table.get_children())
    TableFill(totalMemory, processes)
    processesFrame.after(1000, lambda: updateTable(processes))


def applyfilters(processes):

    global totalMemory
    selectedColumn= selectedOption.get()
    searchedText = entry.get()

    filteredProcesses = []
    for process  in processes:
        try:
            if selectedColumn == 'Name' and searchedText.lower() in process.name().lower():
                filteredProcesses.append(process)
            elif selectedColumn == 'User' and searchedText.lower() in process.username().lower():
                filteredProcesses.append(process)
            elif selectedColumn == 'Status' and searchedText.lower() in process.status().lower():
                filteredProcesses.append(process)
            elif selectedColumn== 'Priority' and searchedText.lower() in str(process.nice()).lower():
                filteredProcesses.append(process)
        except Exception:
            pass
    updateTable(filteredProcesses)



def clearFilters(processes):
    entry.delete(0, tk.END)
    selectedOption.set("Select")
    try:
        table.delete(*table.get_children())
        updateTable(processes)
    except Exception:
        pass


#Main window
root = Tk()
root.title("Resources Manager")
root.geometry("1200x800")


#Notebook
style = ttk.Style()
style.configure("TNotebook.Tab", focuscolor="")
notebook = ttk.Notebook(root, style="TNotebook")
processesFrame = ttk.Frame(notebook)
processesFrame.pack(fill=tk.BOTH, expand=True)
performaceFrame = ttk.Notebook(notebook)
notebook.add(processesFrame, text="Processes")
notebook.add(performaceFrame, text="Performance")
notebook.pack(fill=tk.BOTH, expand=True)


#Table
table = ttk.Treeview(processesFrame)
table['columns'] = ('PID', 'NAME','USER', 'PRIORITY','STATUS', 'CPU', 'MEMORY')
table.heading('PID', text='PID')
table.heading('NAME', text='NAME')
table.heading('USER', text='USER')
table.heading('PRIORITY', text='PRIORITY')
table.heading('STATUS', text='STATUS')
table.heading('CPU', text='CPU')
table.heading('MEMORY',text='MEMORY')
table.column('#0', width=0, stretch=tk.NO)
table.column("PID", width=50)
table.column("PRIORITY", width=70)
for column in table['columns']:
    table.column(column,anchor='center')
totalMemory = psutil.virtual_memory().total
processes = ProcessObtain()
scrollbar = ttk.Scrollbar(processesFrame, orient='vertical', command=table.yview)
table.configure(yscrollcommand=scrollbar.set)
processesFrame.grid_rowconfigure(1, weight=1)
processesFrame.grid_columnconfigure(0, weight=1)
table.grid(row=1,column=0,sticky='nsew')
scrollbar.grid(row=1,column=1,sticky='ns')

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
dropdown = ttk.OptionMenu(container, selectedOption, 'Select','Name', 'User', 'Status', 'Priority')
dropdown.grid(row=0, column=1,sticky="W")

#Filter
entry = tk.Entry(container, width=50)
entry.grid(row=0, column=2, sticky="NSEW")
buttonApply = tk.Button(container, text="Apply", command= lambda: applyfilters(processes))
buttonApply.grid(row=0, column=3, sticky="E")
buttonClear = tk.Button(container, text="Clear filters", command= lambda: clearFilters(processes))
buttonClear.grid(row=0, column=4, sticky="W")



updateTable(processes)
root.mainloop()