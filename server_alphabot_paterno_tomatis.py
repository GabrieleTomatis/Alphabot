### SERVER
import socket
import AlphaBot

keys = ["w", "a", "s", "d"]
last_command = None

robot = AlphaBot.AlphaBot()
robot.stop()

server_address = ("192.168.1.143", 34512)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(server_address)
server_socket.listen(1)
print("Server in attesa...")

def move_direction(command):
    # Prima si controllano le combinazioni di direzioni
    if "w" in command and "d" in command:
        left = -25
        right = 75
    elif "w" in command and "a" in command:
        left = -55
        right = 25
    elif "s" in command and "d" in command:
        left = 55
        right = -25
    elif "s" in command and "a" in command:
        left = 25
        right = -55

    # In seguito, si controllano le direzioni singole
    elif "w" in command:
        right = 55
        left = -35
    elif "s" in command:
        right = -55
        left = 35
    elif "a" in command:
        left = 0
        right = -35
    elif "d" in command:
        left = 35
        right = 0
    
    else:
        left = 0
        right = 0

    robot.setMotor(left, right)

try:
    while True:
        client, addr = server_socket.accept()
        print(f"Connessione stabilita con {addr}")

        while True:
            command = client.recv(4096).decode('utf-8')
            if command == 'stop':
                robot.stop()
                last_command = None

            elif command == 'end':
                client.close()
                break

            elif set(command) & set(keys):
                move_direction(command)
                print(f"Comando ricevuto: {command}")
                last_command = command
                
            elif last_command is None:
                robot.stop()

except KeyboardInterrupt:
    print("Server arrestato manualmente.")
finally:
    server_socket.close()
    print("Server chiuso.")
