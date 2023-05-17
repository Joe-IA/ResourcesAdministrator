from tkinter import *
import tkinter as tk
from tkinter import ttk
from ProcessInfo import ProcessInfo
import psutil




def applyFilters(processes, totalMemory, selectedOption, filteredVar):

    filteredVar.set(True)

  
    selected_column = selectedOption.get()
    
   
    search_text = entry.get()
    

    table.delete(*table.get_children())
    
    
    filtered_processes = []
    for process in processes:
        try:
            if selected_column == 'Name' and search_text.lower() in process.name().lower():
                filtered_processes.append(process)
            elif selected_column == 'User' and search_text.lower() in process.username().lower():
                filtered_processes.append(process)
            elif selected_column == 'Status' and search_text.lower() in process.status().lower():
                filtered_processes.append(process)
            elif selected_column == 'Priority' and search_text.lower() in str(process.nice()).lower():
                filtered_processes.append(process)
        except Exception:
            continue
    

    for process in filtered_processes:
        memoryInfo = process.memory_info()
        physicalMemory = memoryInfo.rss
        table.insert("", tk.END,value=(process.pid, process.name(), process.username(), process.nice(),process.status(), f"{(process.cpu_percent() * 100) / psutil.cpu_count():.2f}%", f"{(physicalMemory / totalMemory * 100):.2f}%"))


def clearFilters(totalMemory, processes, filteredVar):
    filteredVar.set(False)
    startTableUpdate(filteredVar)
    entry.delete(0, tk.END)
    selectedOption.set('Select')
    try:
        table.delete(*table.get_children())
        
        for process in processes:
            memoryInfo = process.memory_info()
            physicalMemory = memoryInfo.rss
            table.insert("", tk.END,value=(process.pid, process.name(), process.username(), process.nice(),process.status(), f"{(process.cpu_percent() * 100) / psutil.cpu_count():.2f}%", f"{(physicalMemory / totalMemory * 100) :.2f}%"))
    except Exception:
        pass


def ProcessObtain():    
    processInfo = ProcessInfo()
    processes = processInfo.getProcesses()
    return processes

def tableFill(totalMemory, processes):
    try:
        for process in processes:
            memoryInfo = process.memory_info()
            physicalMemory = memoryInfo.rss
            table.insert("", tk.END,value=(process.pid, process.name(), process.username(), process.nice(),process.status(), f"{(process.cpu_percent() * 100) / psutil.cpu_count():.2f}%", f"{(physicalMemory / totalMemory * 100) :.2f}%"))
    except:
        pass


def updateTable(filtered):
    global totalMemory, processes
    print(filtered.get())
    if not filtered.get():
        table.delete(*table.get_children())  
        tableFill(totalMemory, processes)    
        processesFrame.after(1000, lambda:updateTable(filtered))
        print("updated")

def startTableUpdate(filtered):
    if not filtered.get():
        updateTable(filtered)
    else:
        processesFrame(1000, lambda: startTableUpdate(filtered))
#Main window
root = Tk()
root.title("Resource manager")
root.geometry("1200x800")

#Notebook
notebook = ttk.Notebook(root)
style = ttk.Style()
style.configure("TNotebook.Tab", focuscolor="")
notebook = ttk.Notebook(root, style="TNotebook")
processesFrame = ttk.Frame(notebook)
processesFrame.pack(fill=tk.BOTH, expand=True)
performanceFrame = ttk.Frame(notebook)
notebook.add(processesFrame, text="Processes")
notebook.add(performanceFrame, text="Performance")
notebook.pack(fill=tk.BOTH, expand=True)

#table
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
container.grid(row=0, column=0)



#Dropdown
selectedOption = tk.StringVar()
dropdown = ttk.OptionMenu(container, selectedOption, 'Select','Name', 'User', 'Status', 'Priority')
dropdown.grid(row=0, column=1)

#Filter
filtered = tk.BooleanVar()
filtered.set(False)

label = tk.Label(container, text='Search: ')
label.grid(row=0, column=0)
entry = tk.Entry(container)
entry.grid(row=0, column=2)
button1 = tk.Button(container, text='Apply', command=lambda:applyFilters(processes, totalMemory, selectedOption, filtered))
button1.grid(row=0, column=3)
button2 = tk.Button(container, text="Delete", command=lambda:clearFilters(totalMemory, processes, filtered))
button2.grid(row=0, column=4)






updateTable(filtered)

root.mainloop()