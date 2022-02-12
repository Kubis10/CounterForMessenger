import os
import json
import glob
from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Counter for messenger")
root.iconbitmap(r'D:\Projekty\CounterForMessenger\assets\CFM.ico')
root.geometry("1024x700")
root.configure(background='#232323')
frm = ttk.Frame(root, padding=10)
frm.grid()
s = ttk.Style()
s.configure('TFrame', background='#131313')
s.configure('TButton', background='#03cafc')
nav = ttk.Frame(root, padding=10, style='s.TFrame')
ttk.Button(nav, text="Wskaż ścieżkę do folderu").grid(row=0, column=0, sticky="ew", padx=5)
ttk.Button(nav, text="Ustawienia").grid(row=1, column=0, sticky="ew", padx=5)
ttk.Button(nav, text="Wyjście", command=root.destroy).grid(row=2, column=0, sticky="ew", padx=5)
nav.grid(row=0, column=0, sticky="ns")
root.mainloop()

ile = 0
numMess = 0


def countPerPerson(data, path):
    global numMess
    totalNum = 0
    participants = []
    result = glob.glob(path + data + '/*.json')
    for j in result:
        with open(j, 'r') as f:
            data = json.load(f)
            for l in data['messages']:
                totalNum += 1
                if l['sender_name'] == "Kuba Przybysz":
                    numMess += 1
            for k in data['participants']:
                if k['name'] not in participants:
                    participants.append(k['name'].encode('iso-8859-1').decode('utf-8'))
            title = data['title'].encode('iso-8859-1').decode('utf-8')
            thread_type = data['thread_type']
    return title, thread_type, totalNum


def countAll(ile, path):
    for i in os.listdir(path):
        conf = countPerPerson(i, path)
        print(conf)
        ile += 1
    print(ile)
    print(numMess)


# countAll(ile, 'data/messages/inbox/')
