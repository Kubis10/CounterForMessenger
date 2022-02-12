import os
import json
import glob
from tkinter import *
from tkinter import ttk

numMess = 0


def countPerPerson(data, path):
    global numMess
    totalNum = 0
    participants = []
    result = glob.glob(path + data + '/*.json')
    for j in result:
        with open(j, 'r') as f:
            data = json.load(f)
            for msg in data['messages']:
                totalNum += 1
                if msg['sender_name'] == "Kuba Przybysz":
                    numMess += 1
            for k in data['participants']:
                if k['name'] not in participants:
                    participants.append(k['name'].encode('iso-8859-1').decode('utf-8'))
            title = data['title'].encode('iso-8859-1').decode('utf-8')
            thread_type = data['thread_type']
    return title, thread_type, totalNum


root = Tk()
root.title("Counter for messenger")
root.iconbitmap(r'D:\Projekty\CounterForMessenger\assets\CFM.ico')
root.geometry("1024x700")
root.configure(background='#232323')
s = ttk.Style()
s.configure('Nav.TFrame', background='#131313')
s.configure('Main.TFrame', background='#232323')
nav = ttk.Frame(root, padding=20, style='Nav.TFrame')
main = ttk.Frame(root, style='Main.TFrame')
home_icon = PhotoImage(file='./assets/home.png')
settings_icon = PhotoImage(file='./assets/settings.png')
exit_icon = PhotoImage(file='./assets/exit.png')
vis_icon = PhotoImage(file='./assets/visible.png')
v = Scrollbar(main)
t = Text(main, width=15, wrap=NONE, yscrollcommand=v.set, background='#232323', foreground='#ffffff')


def countAll(path):
    ile = 0
    for i in os.listdir(path):
        conf = countPerPerson(i, path)
        t.insert('end', str(conf[0]) + " " + str(conf[2]) + '\n')
        ile += 1
    print(ile)
    print(numMess)


ttk.Button(nav, image=home_icon, text="Strona głowna", compound=LEFT, padding=5).pack(side=TOP, pady=10)
ttk.Button(nav, image=vis_icon, text="Pokaż wiadomości", compound=LEFT, padding=5,
           command=lambda: countAll("data/messages/inbox/")).pack(side=TOP, pady=10)
ttk.Button(nav, image=exit_icon, text="Wyjście", compound=LEFT, padding=5, command=root.destroy).pack(side=BOTTOM)
ttk.Button(nav, image=settings_icon, text="Ustawienia", compound=LEFT, padding=5).pack(side=BOTTOM, pady=15)
ttk.Label(main, text="Liczba wiadomości: ", foreground='#ffffff', background='#232323', font=('Arial', 15)).pack(
    side=TOP, pady=10)
v.pack(side=RIGHT, fill=Y)
t.pack(side=TOP, fill=BOTH, expand=True)
v.config(command=t.yview)
nav.pack(side=LEFT, fill=Y)
main.pack(side=RIGHT, fill=BOTH, expand=True)
root.mainloop()
