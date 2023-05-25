import psutil


i = 0

while i < 20:
    netStatus = psutil.net_if_stats()
    print(netStatus)
    i += 1

    