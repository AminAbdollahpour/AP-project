import socket
import tkinter as tk
import json
import time

choice = 0


def get_input():
    global choice
    choice = int(entry.get())
    print(choice)


choose_text = "Choose your action:\n" + "     1. Attack     \n" + "  2. Magic Attack  \n" + "     3. Defend     \n" + "      4. skip      "


def choose_action(report):
    global entry
    entry = tk.Entry(root)
    entry.pack()

    button = tk.Button(root, text="Submit", command=get_input)
    button.pack()
    root.update()

    while True:
        root.update()
        if choice in [1, 2, 3, 4]:
            if choice == 1 and report['Stamina'] < 20:
                message = "Not enough stamina!"
                label2.configure(text=message)

            elif choice == 2 and report['Mana'] < 30:
                message = "Not enough mana!"
                label2.configure(text=message)

            elif choice == 4:
                message = 'You did nothing this round'
                label2.configure(text=message)

                return choice

            else:
                return choice

        else:
            message = 'please enter a number in (1-4)'
            label2.configure(text=message)
        root.update()


PORT = 9090
HOST = '127.0.0.1'
FORMAT = 'utf-8'
SIZE = 1024
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

root = tk.Tk()

root.geometry("500x300+100+100")

status = ""
label = tk.Label(text=status)
label.pack()

label1 = tk.Label(root, text=choose_text)
label1.pack()

error_text = ""
label2 = tk.Label(root, text=error_text)
label2.pack()

root.update()
while True:
    report = client.recv(SIZE).decode(FORMAT)
    report_enemy = client.recv(SIZE).decode(FORMAT)
    root.update()

    status = report + "\n" + report_enemy
    label.configure(text=status)
    root.update()

    report = json.loads(report)
    action = choose_action(report)
    client.sendall(str(action).encode(FORMAT))
    root.update()

    error_text = 'Action Sent.'
    label2.configure(text=error_text)
    root.update()

