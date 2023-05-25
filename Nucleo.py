import psutil

import psutil

def get_num_cores():
    num_cores = psutil.cpu_count(logical=False)
    return num_cores

def get_num_corest():
    num_cores = psutil.cpu_count(logical=True)
    return num_cores

num_cores = get_num_cores()
print("Número de núcleos de la CPU:", num_cores)

num_corest = get_num_corest()
print("Número de núcleos de la CPU:", num_corest)
