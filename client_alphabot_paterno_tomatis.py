### CLIENT
import socket
from pynput import keyboard

keys = ["w", "a", "s", "d", "q"]
pressed_keys = set()
server_address = ("192.168.1.143", 34512)
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)

def handle_press(key):
    if key == "q":
        pressed_keys.clear()
        client_socket.send("stop".encode('utf-8'))
    elif key not in pressed_keys:
        pressed_keys.add(key)
        client_socket.send(("".join(pressed_keys)).encode('utf-8'))

# Al rilascio dei tasti il client invia nuovamente i comandi (utile per gestire la frenata e il cambio di direzione)
def handle_release(key):
    if key in pressed_keys:
        pressed_keys.remove(key)
        if pressed_keys:
            client_socket.send(("".join(pressed_keys)).encode('utf-8'))
        else:
            client_socket.send("stop".encode('utf-8'))

def on_press(key):
    try:
        if key.char in keys:
            handle_press(key.char)
            print(f"Tasto premuto: {key.char}")
    except AttributeError:
        if key == keyboard.Key.esc:
            client_socket.send("end".encode('utf-8'))  # Termina la connessione se Esc viene premuto

def on_release(key):
    try:
        if key.char in keys:
            handle_release(key.char)
    except AttributeError:
        pass

with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

client_socket.close()