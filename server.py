import socket  # Pour les connexions réseau
import threading  # Pour gérer plusieurs clients en même temps (un thread par client)
import json  # Pour sauvegarder les données (UUID et clés) dans un fichier simple
import os  # Pour vérifier les fichiers et dossiers
import logging  # Pour les logs (bonus)
import datetime  # Pour horodatage des logs
import secrets  # Pour générer token aléatoire (auth bonus)

# Config logs simple (fichier server.log, format avec time/level)
logging.basicConfig(filename='/home/hugo/PROJET/server/server.log', level=logging.INFO, 
                    format='[%(asctime)s] [%(levelname)s] %(message)s')

# Fonction pour charger les données sauvegardées (comme un "fichier de config")
def load_storage():
    fichier_storage = '/home/hugo/PROJET/server/storage.json'  # Nom du fichier simple
    if os.path.exists(fichier_storage):  # Si le fichier existe
        with open(fichier_storage, 'r') as f:  # Ouvre et lit
            return json.load(f)  # Transforme en dictionnaire Python
    return {}  # Sinon, retourne un dictionnaire vide

# Fonction pour sauvegarder les données
def save_storage(storage):
    with open('/home/hugo/PROJET/server/storage.json', 'w') as f:  # Ouvre et écrit
        json.dump(storage, f)  # Transforme le dictionnaire en JSON

# Fonction simple pour recevoir une ligne (comme dans les exercices, byte par byte pour simplicité)
def recv_line(sock):
    data = b""  # Commence avec vide
    while not data.endswith(b"\n"):  # Tant que pas de fin de ligne
        chunk = sock.recv(1)  # Reçoit 1 byte à la fois (simple mais lent, OK pour débutant)
        if not chunk:  # Si rien, connexion fermée
            return None
        data += chunk  # Ajoute
    return data.decode("utf-8").strip()  # Transforme en texte et enlève espaces

# Fonction pour recevoir exactement n bytes (comme dans exercices)
def recv_exact(sock, n):
    data = b""  # Vide
    while len(data) < n:  # Tant que pas assez
        chunk = sock.recv(min(4096, n - len(data)))  # Reçoit un bloc (max 4096)
        if not chunk:  # Si rien, erreur
            return None
        data += chunk  # Ajoute
    return data

# Fonction pour gérer un client (lancée dans un thread)
def handle_client(client_sock, storage, active_clients):
    logging.info("Nouveau client connecté.")  # Log info
    print("Nouveau client connecté.")  # Message console
    uuid = None  # Pour stocker UUID plus tard
    try:
        while True:  # Boucle pour recevoir des messages
            cmd = recv_line(client_sock)  # Reçoit la commande comme ligne
            if cmd is None:  # Si rien, client déconnecté
                break
            if cmd == "REGISTER":  # Si enregistrement (pas d'auth pour REGISTER)
                uuid = recv_line(client_sock)  # Reçoit UUID
                key = recv_line(client_sock)  # Reçoit clé
                token = secrets.token_hex(16)  # Génère token aléatoire (32 chars hex, simple)
                storage[uuid] = {"key": key, "token": token}  # Stocke clé + token
                save_storage(storage)  # Sauvegarde
                active_clients[uuid] = client_sock  # Ajoute au liste des actifs
                send_line(client_sock, token)  # Envoie token au client
                logging.info(f"Client enregistré: UUID={uuid}, Key={key}, Token={token}")  # Log
                print(f"Client enregistré: UUID={uuid}, Key={key}")
            else:  # Pour autres commandes, vérifier auth
                if uuid is None or uuid not in storage:  # Pas encore enregistré
                    logging.error("Commande sans register.")  # Log error
                    send_line(client_sock, "ERROR")
                    send_line(client_sock, "Register first")
                    break
                token_received = cmd  # Première ligne après REGISTER est token pour auth
                if token_received != storage[uuid]["token"]:  # Vérifie token
                    logging.error(f"Auth échouée pour UUID={uuid}")  # Log
                    send_line(client_sock, "ERROR")
                    send_line(client_sock, "Invalid token")
                    break
                cmd = recv_line(client_sock)  # Reçoit la vraie commande après token
                logging.info(f"Commande reçue de {uuid}: {cmd}")  # Log commande
                
                if cmd == "OUTPUT":  # Sortie de commande
                    taille = int(recv_line(client_sock))  # Reçoit taille
                    output = recv_exact(client_sock, taille).decode()  # Reçoit données
                    print(f"Output: {output}")
                    logging.info(f"Output reçu: {output}")
                elif cmd == "ERROR":  # Erreur
                    taille = int(recv_line(client_sock))  # Taille
                    error = recv_exact(client_sock, taille).decode()
                    print(f"Erreur client: {error}")
                    logging.error(f"Erreur client: {error}")
                elif cmd == "FILE":  # Fichier upload
                    file_name = recv_line(client_sock)  # Nom
                    taille = int(recv_line(client_sock))  # Taille
                    file_data = recv_exact(client_sock, taille)  # Données
                    with open(f"uploaded_{file_name}", "wb") as f:  # Sauvegarde
                        f.write(file_data)
                    print(f"Fichier reçu: {file_name}")
                    logging.info(f"Fichier reçu: {file_name}")
                elif cmd == "OK":  # Confirmation
                    msg = recv_line(client_sock)
                    print(f"OK: {msg}")
                    logging.info(f"OK: {msg}")
                elif cmd == "READY":  # Prêt pour download (mais géré dans console)
                    pass  # Rien ici, console enverra après
                else:
                    logging.warning("Commande inconnue.")  # Log warning
                    print("Commande inconnue.")
    except Exception as e:
        logging.error(f"Erreur avec client: {e}")  # Log error
        print(f"Erreur avec client: {e}")
    finally:
        if uuid in active_clients:
            del active_clients[uuid]  # Enlève si déconnecté
        client_sock.close()  # Ferme toujours
        logging.info("Client déconnecté.")

# Fonction pour la console du serveur (lancée dans un thread)
def console(storage, active_clients):
    print("Console active. Ex: send uuid EXEC ls")
    print("Ou list, quit")
    while True:
        input_cmd = input("> ")
        if input_cmd == "quit":
            os._exit(0)  # Arrête tout
        elif input_cmd == "list":
            print("UUID enregistrés:")
            for uuid in storage:
                print(uuid)
        elif input_cmd.startswith("send "):
            parts = input_cmd.split(" ", 3)  # Split simple
            if len(parts) < 3:
                print("Format: send uuid commande args")
                continue
            uuid = parts[1]
            cmd = parts[2]
            args = parts[3] if len(parts) > 3 else ""
            if uuid not in active_clients:
                print("UUID pas connecté")
                continue
            sock = active_clients[uuid]
            logging.info(f"Envoi commande à {uuid}: {cmd} {args}")  # Log envoi
            if cmd == "EXEC":
                sock.sendall((cmd + "\n" + args + "\n").encode())  # Envoi simple
            elif cmd == "UPLOAD":
                sock.sendall((cmd + "\n" + args + "\n").encode())
            elif cmd == "DOWNLOAD":
                if not os.path.exists(args):
                    print("Fichier pas trouvé")
                    continue
                with open(args, "rb") as f:
                    data = f.read()
                sock.sendall((cmd + "\n" + args + "\n").encode())  # Commande
                # Attends READY? Pour simple, assume client prêt
                taille_str = str(len(data)) + "\n"
                sock.sendall(taille_str.encode() + data)  # Envoi taille + data
            elif cmd == "CRYPTO":
                mode, path = args.split(" ", 1)  # Split mode path
                sock.sendall((cmd + "\n" + mode + "\n" + path + "\n").encode())
            else:
                print("Commande invalide")
        else:
            print("Commande inconnue")

# Fonction envoi ligne simple (utilisée dans handle_client)
def send_line(sock, msg):
    sock.sendall((msg + "\n").encode())  # Envoi avec \n

# Partie principale
if __name__ == "__main__":
    HOST = ""  # Toutes interfaces
    PORT = 4444
    storage = load_storage()
    active_clients = {}
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    logging.info("Serveur démarré.")  # Log start
    print(f"Serveur sur port {PORT}")

    console_thread = threading.Thread(target=console, args=(storage, active_clients))
    console_thread.start()

    while True:
        client_sock, addr = server.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_sock, storage, active_clients))
        client_thread.start()