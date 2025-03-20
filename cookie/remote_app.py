from flask import Flask, render_template, request, redirect, url_for, make_response
import jwt
import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

from alphaLib import AlphaBot
robot = AlphaBot()
robot.setMotor(0, 0)  #Fermo i motori all'avvio

app = Flask(__name__)
app.secret_key = "secret_key_paterno_tomatis"

JWT_SECRET_KEY = "secret_key_paterno_tomatis_token"

#Creo un token JWT che contiene il nome dell'utente e una data di scadenza
def generate_token(username):
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=1) #Imposto la data di scadenza del token
    payload = {"username": username, "exp": expiration_time}  #Creo il payload del token
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm="HS256")  #Ritorno il token codificato

#Verifico la validità del token JWT decodificandolo e controllando la sua scadenza
def verify_token(token):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])  #Decodifico il token
        return payload["username"]  #Ritorno il nome utente se il token è valido
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):  #Gestisco i casi in cui il token è scaduto o invalido
        return None

#Mi connetto al database SQLite per eseguire operazioni
def get_db_connection():
    conn = sqlite3.connect('utenti.db')  #Mi connetto al database
    conn.row_factory = sqlite3.Row  #Imposto il cursore per ottenere righe come dizionari
    return conn

#Creo la tabella 'users' se non esiste già nel database
def create_user_table():
    conn = get_db_connection()  #Ottengo la connessione al database
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')  #Creo la tabella 'users' con i campi id, username e password
    conn.commit()  #Salvo le modifiche nel database
    conn.close()  #Chiudo la connessione al database

create_user_table()  #Chiamo la funzione per creare la tabella al lancio dell'app

#Aggiungo un nuovo utente al database dopo aver criptato la password
def add_user(username, password):
    conn = get_db_connection()  #Mi connetto al database
    hashed_password = generate_password_hash(password)  #Cripto la password prima di salvarla
    try:
        conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))  #Inserisco il nuovo utente nel database
        conn.commit()  #Salvo le modifiche
    except sqlite3.IntegrityError:  #Gestisco il caso in cui lo username è già presente
        return False
    finally:
        conn.close()  #Chiudo la connessione al database
    return True  #Ritorno True se l'utente è stato aggiunto con successo

#Recupero le informazioni di un utente dal database dato il suo username
def get_user(username):
    conn = get_db_connection()  #Mi connetto al database
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()  #Recupero l'utente con lo username dato
    conn.close()  #Chiudo la connessione al database
    return user  #Ritorno l'utente trovato

@app.route("/", methods=["GET", "POST"])
def login():
    token_cookie = request.cookies.get("mycookie")  #Controllo se esiste un cookie con il token dell'utente
    if token_cookie and verify_token(token_cookie):  #Se il token è valido, vado direttamente alla home
        return redirect(url_for("home"))
    
    if request.method == "POST":  #Se l'utente invia il form di login
        username = request.form["username"]  #Recupero lo username dal form
        password = request.form["password"]  #Recupero la password dal form

        user = get_user(username)  #Recupero l'utente dal database
        if user and check_password_hash(user["password"], password):  #Verifico che la password corrisponda
            token = generate_token(username)  #Se le credenziali sono corrette, genero un token
            resp = make_response(redirect(url_for("home")))  #Creo una risposta con il redirect alla home
            resp.set_cookie("mycookie", token, max_age=60*60*24)  #Imposto il cookie con il token
            return resp
        else:
            return render_template("login.html", alert="Credenziali errate")  #Se le credenziali sono errate, mostro un messaggio di errore
    
    return render_template("login.html")  #Se la richiesta è GET, mostro il modulo di login

@app.route("/create_account", methods=["GET", "POST"])
def create_account():
    if request.method == "POST":  #Se l'utente invia il form di registrazione
        username = request.form["username"]  #Recupero lo username dal form
        password = request.form["password"]  #Recupero la password dal form
        
        if add_user(username, password):  #Aggiungo il nuovo utente al database
            return redirect(url_for("login"))  #Dopo la registrazione, redirigo al login
        else:
            return render_template("create_account.html", alert="Username già esistente")  # Se lo username è già presente, mostro un errore
    
    return render_template("create_account.html")  #Se la richiesta è GET, mostro il modulo di registrazione

@app.route("/home")
def home():
    token = request.cookies.get("mycookie")  #Recupero il token dal cookie
    if token and verify_token(token):  #Se il token è valido
        username = verify_token(token)  #Recupero il nome utente dal token
        return render_template("home.html", username=username)  #Mostro la pagina home con il nome utente
    
    resp = make_response(redirect(url_for("login")))  #Se il token non è valido, redirigo al login
    resp.delete_cookie("mycookie")  #Elimino il cookie del token
    return resp

@app.route("/command", methods=["POST"])
def command():
    token = request.cookies.get("mycookie")  #Recupero il token dal cookie
    if not token or not verify_token(token):  #Se il token non è presente o non è valido
        return "Unauthorized", 401  #Ritorno un errore di autorizzazione

    command = request.form.get("cmd")  # Recupero il comando dal form

    print("Comando ricevuto: ", command)
    
    if command == "forward":
        left = -45
        right = 55
    elif command == "backward":
        left = 45
        right = -55
    elif command == "left":
        left = 0
        right = -35
    elif command == "right":
        left = 35
        right = 0
    elif command == "stop":  #Se il comando è stop, fermo i motori
        left = 0
        right = 0
    else:
        left = 0
        right = 0  #Se il comando non è riconosciuto, fermo tutto

    robot.setMotor(left, right)  #Invio i valori dei motori al robot per eseguire il comando
    
    return "OK", 200  #Rispondo con un OK

@app.route("/logout")
def logout():
    resp = make_response(redirect(url_for("login")))  #Creo una risposta con il redirect al login
    resp.delete_cookie("mycookie")  #Elimino il cookie del token
    return resp  #Ritorno la risposta con il logout effettuato

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)  #Avvio il server Flask in modalità debug
