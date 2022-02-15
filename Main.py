import os
import json
import glob
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

numMess = 0
pathDir = 'data/messages/inbox/'
username = "Kuba Przybysz"


def openLoading(lenNum):
    Window = Toplevel(root)
    Window.title("Ładowanie...")
    Window.geometry("300x100")
    Window.resizable(False, False)
    Window.focus_set()
    Window.grab_set()
    progress = ttk.Progressbar(Window, orient="horizontal", maximum=int(lenNum), length=200, mode="determinate")
    label = ttk.Label(Window, text="Ładowanie konwersacji 0/"+str(lenNum))
    progress.pack(side=TOP)
    label.pack(side=TOP)
    return progress, label, Window


def countPerPerson(data, path, uname):
    global numMess
    totalNum = 0
    callTime = 0
    participants = []
    result = glob.glob(path + data + '/*.json')
    for j in result:
        with open(j, 'r') as f:
            data = json.load(f)
            for msg in data['messages']:
                totalNum += 1
                if msg['sender_name'] == uname:
                    numMess += 1
                if msg['type'] == 'Call':
                    callTime += msg['call_duration']
            for k in data['participants']:
                if k['name'] not in participants:
                    participants.append(k['name'].encode('iso-8859-1').decode('utf-8'))
            title = data['title'].encode('iso-8859-1').decode('utf-8')
            thread_type = data['thread_type']
            if thread_type == "Regular":
                thread_type = "Czat Prywatny"
            elif thread_type == "RegularGroup":
                thread_type = "Grupa"

    return title, participants, thread_type, totalNum, callTime


def treeview_sort_msg(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(key=lambda t: int(t[0]), reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col,
               command=lambda: treeview_sort_msg(tv, col, not reverse))


def treeview_sort_column(tv, col, reverse):
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


def search():
    query = search_entry.get()
    selections = []
    for child in t.get_children():
        for i in t.item(child)['values']:
            if str(i).find(query) != -1:
                selections.append(child)
    print('znaleziono: ', len(selections))
    t.selection_set(selections)


def countAll(path, uname):
    t.delete(*t.get_children())
    x, label, window = openLoading(len(os.listdir(path)))
    for i in os.listdir(path):
        try:
            conf = countPerPerson(i, path, uname)
            t.insert(parent='', index=END, values=(conf[0], conf[1], conf[2], conf[3], conf[4]))
        except Exception as e:
            print(e)
            continue
        x['value'] += 1
        x.update()
        label['text'] = "Ładowanie konwersacji " + str(int(x['value'])) + "/" + str(len(os.listdir(path)))
        label.update()
    window.destroy()
    t.heading('msg', command=lambda _col='msg': treeview_sort_msg(t, _col, False))
    t.heading('name', command=lambda _col='name': treeview_sort_column(t, _col, False))
    t.heading('type', command=lambda _col='type': treeview_sort_column(t, _col, False))
    t.heading('call', command=lambda _col='call': treeview_sort_msg(t, _col, False))
    print(len(os.listdir(path)))
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
t['columns'] = ('name', 'pep', 'type', 'msg', 'call')
t.heading("name", text="Nazwa", anchor=CENTER)
t.heading("pep", text="Uczestnicy", anchor=CENTER)
t.heading("type", text="Typ", anchor=CENTER)
t.heading("type", text="Typ", anchor=CENTER)
t.heading("msg", text="Liczba wiadomości", anchor=CENTER)
t.heading("call", text="Łączna długość rozmów", anchor=CENTER)
ttk.Button(nav, image=home_icon, text="Strona główna", compound=LEFT, padding=5).pack(side=TOP, pady=10)
ttk.Button(nav, image=vis_icon, text="Pokaż wiadomości", compound=LEFT, padding=5,
           command=lambda: countAll(pathDir, username)).pack(side=TOP, pady=10)
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
