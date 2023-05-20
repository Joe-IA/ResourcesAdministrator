import psutil


class ProcessInfo:
    def __init__(self):
        self.processes = psutil.process_iter()

    def getProcesses(self):
        return list(self.processes)
    
if __name__ == '__main__':
    #info = ProcessInfo()
    #i = 0
    #for proceso in info.getProcess():
     #print(proceso.cpu_percent() * 100.0 / psutil.cpu_count())


    info = ProcessInfo()
    processes = info.getProcesses()

    users = {
    }
    count = 0
    for process in processes:
        if process.username() not in users:
            users[process.username()] = count
            usersMemory = [0 for i in range(len(users))]
            usersProcessor = [0 for i in range(len(users))]            
            #usersSwap = [0 for i in range(len(users))]
            count +=1
    print(users)
    for process in processes:
        
        cpuPercentage = (process.cpu_percent() * 100) / psutil.cpu_count()
        usersMemory[users[process.username()]] += process.memory_info().rss / psutil.virtual_memory().total
        usersProcessor[users[process.username()]] += cpuPercentage
        #usersSwap[users[process.name()]] += process.memory_info().swap


    arrayNames = [clave for clave in users.keys()]

    for i in range(len(arrayNames)):
        print(arrayNames[i])
        print(f"{usersMemory[i] * 100 :.2f} %")
        print(f"{usersProcessor[i]:.2f} %")
        #print(f"{usersSwap[i] * 100 :.2f} %")
        