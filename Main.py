import os
import json
import glob
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

numMess = 0
pathDir = 'data/messages/inbox/'


def countPerPerson(data, path, uname):
    global numMess
    totalNum = 0
    participants = []
    result = glob.glob(path + data + '/*.json')
    for j in result:
        with open(j, 'r') as f:
            data = json.load(f)
            for msg in data['messages']:
                totalNum += 1
                if msg['sender_name'] == uname:
                    numMess += 1
            for k in data['participants']:
                if k['name'] not in participants:
                    participants.append(k['name'].encode('iso-8859-1').decode('utf-8'))
            title = data['title'].encode('iso-8859-1').decode('utf-8')
            thread_type = data['thread_type']
    return title, participants, thread_type, totalNum


def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(key=lambda t: int(t[0]), reverse=reverse)

    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)

    tv.heading(col,
               command=lambda: treeview_sort_column(tv, col, not reverse))


def search():
    query = search_entry.get()
    selections = []
    for child in t.get_children():
        for i in t.item(child)['values']:
            if str(i).find(query) != -1:
                selections.append(child)
    print('znaleziono: ', len(selections))
    t.selection_set(selections)


def countAll(path):
    ile = 0
    for i in os.listdir(path):
        try:
            conf = countPerPerson(i, path, "Kuba Przybysz")
            t.insert(parent='', index=END, values=(conf[0], conf[1], conf[2], conf[3]))
        except Exception as e:
            print(e)
            continue
        ile += 1
    t.heading('msg', command=lambda _col='msg': treeview_sort_column(t, _col, False))
    print(ile)
    print(numMess)


def SelectDir():
    global pathDir
    pathDir = filedialog.askdirectory() + "/"
    print(pathDir)


root = Tk()
root.title("Counter for messenger")
root.iconbitmap(r'assets\CFM.ico')
root.geometry("1024x700")
root.configure(background='#232323')
s = ttk.Style()
s.configure('Nav.TFrame', background='#131313')
s.configure('Main.TFrame', background='#232323')
s.configure('Custom.Treeview', background='#232323', foreground='#ffffff')
nav = ttk.Frame(root, padding=20, style='Nav.TFrame')
main = ttk.Frame(root, style='Main.TFrame')
home_icon = PhotoImage(file='./assets/home.png')
settings_icon = PhotoImage(file='./assets/settings.png')
exit_icon = PhotoImage(file='./assets/exit.png')
vis_icon = PhotoImage(file='./assets/visible.png')
inv_icon = PhotoImage(file='./assets/invisible.png')
search_icon = PhotoImage(file='./assets/search.png')
v = Scrollbar(main)
t = ttk.Treeview(main, height=20, yscrollcommand=v.set, style='Custom.Treeview')
t.column("#0", width=0, stretch=NO)
t['columns'] = ('name', 'pep', 'type', 'msg')
t.heading("name", text="Nazwa", anchor=CENTER)
t.heading("pep", text="Uczestnicy", anchor=CENTER)
t.heading("type", text="Typ", anchor=CENTER)
t.heading("type", text="Typ", anchor=CENTER)
t.heading("msg", text="Liczba wiadomości", anchor=CENTER)
ttk.Button(nav, image=home_icon, text="Strona główna", compound=LEFT, padding=5).pack(side=TOP, pady=10)
ttk.Button(nav, image=vis_icon, text="Pokaż wiadomości", compound=LEFT, padding=5,
           command=lambda: countAll(pathDir)).pack(side=TOP, pady=10)
search_entry = ttk.Entry(nav, width=15)
search_entry.pack(side=TOP, pady=10)
ttk.Button(nav, image=search_icon, text="Szukaj", compound=LEFT, command=search).pack(side=TOP, pady=10)
ttk.Button(nav, image=exit_icon, text="Wyjście", compound=LEFT, padding=5, command=root.destroy).pack(side=BOTTOM)
ttk.Button(nav, image=settings_icon, text="Ustawienia", compound=LEFT, padding=5, command=SelectDir).pack(side=BOTTOM, pady=15)
ttk.Label(main, text="Liczba wiadomości: ", foreground='#ffffff', background='#232323', font=('Arial', 15)).pack(
    side=TOP, pady=10)
v.pack(side=RIGHT, fill=Y)
t.pack(side=LEFT, fill=BOTH, expand=1)
v.config(command=t.yview)
nav.pack(side=LEFT, fill=Y)
main.pack(side=RIGHT, fill=BOTH, expand=True)
if __name__ == '__main__':

    root.mainloop()
