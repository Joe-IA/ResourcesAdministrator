import psutil


class ProcessInfo:
    def __init__(self):
        self.processes = psutil.process_iter()

    def getProcesses(self):
        return list(self.processes)
    
if __name__ == '__main__':
    info = ProcessInfo()
    i = 0
    for proceso in info.getProcess():
     print(proceso.cpu_percent() * 100.0 / psutil.cpu_count())
