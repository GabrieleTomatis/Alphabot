import socket

BUFFER_SIZE = 4096
server_address = ("127.0.0.1", 6980)

def riceviComando(comando):
    print(f"Comando ricevuto: '{comando}'")
    valori = comando.strip().split(",")  # Rimuovo spazi e divido la stringa

    if len(valori) != 2:
        print("Input non valido")
        return

    try:
        direzione = int(float(valori[0]))  # Conversione in intero della direzione
        distanza = int(float(valori[1]))   # Conversione in intero della distanza
    except ValueError:
        print("Errore: impossibile convertire i valori")
        return

    # Controllo che la distanza sia tra 1 e 100
    if distanza < 1 or distanza > 100:
        print("Il valore deve essere un valore compreso tra 1 e 100")
    elif direzione == 1:
        print(f"avanti di {distanza}")
    elif direzione == 2:
        print(f"indietro di {distanza}")
    elif direzione == 3:
        print(f"destra di {distanza}")
    elif direzione == 4:
        print(f"sinistra di {distanza}")
    else:
        print("Comando non valido")
    

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(server_address)
    s.listen()
    
    print("Server in ascolto...")
    connection, client_address = s.accept()  # Bloccante
    print(f"Client: {client_address}")

    while True:
        risposta = connection.recv(BUFFER_SIZE)
        
        riceviComando(risposta.decode())

    connection.close()

if __name__ == "__main__":
    main()