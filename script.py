#!/usr/bin/python3

import requests
import json
import subprocess
import datetime
#
# Monitoring Upload
#

who = requests.get('http://localhost:5000/who')
os = requests.get('http://localhost:5000/os/kernel')
swap = requests.get('http://localhost:5000/swap/so')
mem = requests.get('http://localhost:5000/mem/free')
cpu = requests.get('http://localhost:5000/cpu/sy')
disk = requests.get ('http://localhost:5000/partition')
uploadtime = {'tiempoSubida' :'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())}
dicSwap = swap.json()
dicWho = who.json()
dicOs = os.json()
dicMem = mem.json()
dicCpu = cpu.json()
dicDisk = disk.json()
payload = {**dicWho, **dicOs, **dicSwap, **dicMem, **dicCpu, **dicDisk, **uploadtime}
print (payload)
postdisk = requests.post('https://manager-system.herokuapp.com/monitoreo', json = payload)
print (postdisk.status_code)

#
# Transmission Magnetlinks requests
#

urls = requests.get('https://manager-system.herokuapp.com/get-descargas')
dicUrls = urls.json()
values = dicUrls.values()
for magnet in values:
    subprocess.check_output(["transmission-remote",'--auth', 'transmission:transmission',"-a", magnet])

#
# Transmission Magnetlinks status
#

keys = ['ID', 'progreso', 'descargado', 'tamaño' ,'tiempoEstimado', 'velocidad', 'velocidadb', 'ratio', 'estado', 'nombre']
keysN = ['ID', 'progreso', 'descargado' ,'tiempoEstimado', 'velocidad', 'velocidadb', 'ratio', 'estado', 'nombre']
keysA = ['ID', 'progreso', 'descargado', 'tamaño', 'tiempoEstimado', 'velocidad', 'velocidadb', 'ratio', 'estado', 'estado2', 'estado3', 'nombre']
def list (value):
    transmission = subprocess.Popen(['transmission-remote' , '--auth', 'transmission:transmission', '-l'],stdout = subprocess.PIPE)
    tail = subprocess.Popen(['tail', '-n' , '+2'], stdin = transmission.stdout,stdout = subprocess.PIPE)
    tr = subprocess.Popen(['tr', '-s' , ' '], stdin = tail.stdout, stdout = subprocess.PIPE)
    output = subprocess.check_output(['cut' , '-d', '\n', '-f', str(value)], stdin = tr.stdout).decode('utf-8').strip()
    return output



def generate():
    x = 1
    uploadtime = {'tiempoSubida' :'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())}
    payload = []
    while True:
        aux = list(x)
        if ((aux.find("Sum:")) != -1)  :
            break
        else:
            x += 1
        data = {**uploadtime}
        print (data)
        if ((aux.find("Up & Down")) != -1):
            values = aux.split(" ")
            for i in range (0 , 11):
                data[keysA[i]] = values[i]
        elif ((aux.find("None")) != -1):
            values = aux.split(" ")
            for j in range (0, 9):
                data[keysN[j]] = values[j]
        else:
            values = aux.split(" ")
            for j in range (0, 10):
                data[keys[j]] = values[j]              
        print (data)
        payload.append(data)
    return payload


post = requests.post('https://manager-system.herokuapp.com/estado', json = generate())
print (post.status_code)
