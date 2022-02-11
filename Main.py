import os
import json
import glob
from tkinter import *
from tkinter import ttk

root = Tk()
root.title("Counter for messenger")
root.iconbitmap(r'D:\Projekty\CounterForMessenger\assets\CFM.ico')
root.geometry("900x600")
frm = ttk.Frame(root, padding=10)
frm.grid()
ttk.Label(frm, text="Hello World!").grid(column=0, row=0)
ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
root.mainloop()

ile = 0


def countPerPerson(data, path):
    totalNum = 0
    parcipants = []
    result = glob.glob(path + data + '/*.json')
    for j in result:
        with open(j, 'r') as f:
            data = json.load(f)
            for l in data['messages']:
                totalNum += 1
            for k in data['participants']:
                if k['name'] not in parcipants:
                    parcipants.append(k['name'].encode('iso-8859-1').decode('utf-8'))
            title = data['title'].encode('iso-8859-1').decode('utf-8')
            thread_type = data['thread_type']
    return title, thread_type, totalNum


def countAll(ile, path):
    for i in os.listdir(path):
        conf = countPerPerson(i, path)
        print(conf)
        ile += 1
    print(ile)


# countAll(ile, 'data/messages/inbox/')
