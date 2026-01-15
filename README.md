# 🛡️ Projet Ransomware Pédagogique en Python (Fait par Hugo Le boulanger et Tony Dias)

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Security](https://img.shields.io/badge/Security-Offensive-red.svg)](#)
[![Educational](https://img.shields.io/badge/Purpose-Educational-green.svg)](#)

Ce projet est réalisé dans le cadre du module **"Introduction a l'écriture d'un malware en Python"**. Il simule le comportement d'un ransomware moderne à des fins éducatives.

> [!CAUTION]
> **AVERTISSEMENT :** Ce code est destiné à un usage strictement pédagogique en environnement contrôlé ici sur VM debian. **Ne l'exécutez jamais sur votre machine physique**. Utilisez exclusivement une Machine Virtuelle (VM) isolée.

### Objectifs pédagogiques
* **Comprendre** l'architecture générale d'un ransomware.
* **Manipuler** les fichiers et répertoires en Python.
* **Implémenter** un chiffrement réversible simple.
* **Concevoir** un protocole client/serveur basique.
* **Structurer** un code de type malware de manière modulaire.
* **Analyser** les faiblesses d'un ransomware artisanal.

### Structure du projet
Le projet est divisé en deux parties :
1. **Partie 1 – Fonctionnalités de base (obligatoire) :** Implémentées ici.
2. **Partie 2 – Fonctionnalités bonus :** Logs et authentification ajoutés.

Ce dépôt contient deux fichiers principaux : `client.py` (le malware) et `server.py` (le serveur de contrôle - C2).

---

## ⚙️ Principe de Fonctionnement

* **Architecture :** Client-serveur TCP (port 4444).
* **Le client (malware) :** S'exécute sur la "victime" : génère une clé, chiffre un dossier, exfiltre UUID/clé vers le serveur, puis écoute des commandes.
* **Le serveur (C2) :** Gère les connexions multi-clients (via threads), stocke les infos (JSON), et permet d'envoyer des commandes via une console interactive.
* **Protocole :** Simple, avec envois de lignes terminées par `\n`. Authentification par token pour les bonus.
* **Chiffrement :** XOR réversible (appliqué sur fichiers binaires, récursif via `os.walk`).
* **Persistence :** Clé/UUID stockés en JSON sur le serveur.
* **Faiblesses :** XOR faible (facile à casser), pas de persistence avancée, pas d'obfuscation, limité à localhost pour tests.
### Schéma de Communication
```text
[ Victime (Client) ]                        [ Serveur (C2) ]
        |                                          |
        |---- REGISTER (UUID + Clé) -------------->| (Stockage JSON)
        |                                          |
        |<--- TOKEN (Authentification) ------------|
        |                                          |
        |<--- COMMAND (EXEC, UPLOAD, CRYPTO...) ---| (Console Admin)
        |                                          |
        |---- RESPONSE (Output, File) ------------>|
```
## 📁 Fichiers du Projet
### 1. `client.py` (Le Malware)
**Description :** Simule le ransomware sur la machine victime.
* **Génère** une clé aléatoire (A-Z majuscules via `/dev/urandom`).
* **Récupère** l'UUID de la machine.
* **Chiffre** récursivement un dossier cible (ex. : `/home/hugo/Documents/MADI/Cible_projet`) avec XOR (réversible).
* **Se connecte** au serveur, envoie l'UUID + la clé.
* **Reçoit** un token d'authentification.
* **Boucle infinie** pour exécuter les commandes reçues (avec vérification du token).
* **Gère** les erreurs et les logs (bonus).
* **Dépendances :** Modules standards (`os`, `socket`, `subprocess`, `logging`).
* **Lancement :** `python3 client.py` (chiffre le dossier, puis écoute).

### 2. `server.py` (Le Serveur de Contrôle - C2)
**Description :** Gère les clients connectés et envoie des commandes.
* **Écoute** sur le port 4444, gère le multi-clients via threads.
* **Reçoit et stocke** l'UUID/clé/token en JSON (`storage.json`).
* **Génère** un token d'authentification pour chaque client.
* **Console interactive** pour lister les clients et envoyer des commandes.
* **Vérifie** l'authentification pour chaque commande envoyée.
* **Gère** les réponses (output, fichiers, erreurs) et les logs horodatés (bonus).
* **Dépendances :** Modules standards (`socket`, `threading`, `json`, `os`, `logging`, `secrets`).
* **Lancement :** `python3 server.py` (démarre l'écoute et la console).

---

## 🛠️ Commandes Possibles (Console C2)
Après lancement de `server.py`, une console s'affiche (`> prompt`).

### Commandes Générales
* `quit` : Arrête le serveur.
* `list` : Liste les UUID enregistrés et connectés.

### Commandes Clients
**Format :** `send <uuid> <commande> [args]`

| Commande | Usage | Description |
| :--- | :--- | :--- |
| **EXEC** | `EXEC <cmd>` | Exécute une commande système (ex. : `ls -l`). |
| **UPLOAD** | `UPLOAD <path>` | Récupère un fichier du client (sauvegardé en `uploaded_...`). |
| **DOWNLOAD** | `DOWNLOAD <path>` | Envoie un fichier du serveur vers le client. |
| **CRYPTO** | `CRYPTO <mode> <path>` | Chiffre/Déchiffre un dossier (mode : `encrypt` ou `decrypt`). |

---

## 🚀 Installation et Utilisation
1.  **Clone le repo :** `git clone <url-github>`
2.  **Préparation :** Crée un dossier cible pour les tests (ex. : `/home/hugo/Documents/MADI/Cible_projet` avec des fichiers factices).
3.  **Lancement Serveur :** `cd server && python3 server.py`
4.  **Lancement Client :** `cd client && python3 client.py`
5.  **Interaction :** Utilise la console du serveur pour interagir avec le client.
6.  **Vérification :** Analyse les logs (`client.log`, `server.log`) et le fichier `storage.json` pour suivre les traces.

**Prérequis :** Python 3, VM Linux (testé sur Debian/Ubuntu).

---

## 📈 Bonus & Analyses

### Bonus Implémentés
* ✅ **Logs horodatés** (INFO/ERROR) exportés dans des fichiers.
* ✅ **Authentification par token** généré de manière sécurisée par le serveur.
* ✅ **Threading** pour la gestion simultanée des clients et de la console.

### Faiblesses et Améliorations Potentielles
* **Cryptographie :** XOR est faible et facile à casser via analyse fréquentielle.
* **Réseau :** Limité à localhost pour les tests ; pas de gestion de reconnexion automatique.
* **Furtivité :** Pas de persistence avancée ni d'obfuscation du code.
* **Améliorations suggérées :** Ajouter des dossiers dédiés pour les fichiers (exfiltrations), support de l'upload via ICMP (via `scapy`), et gestion multi-fichiers améliorée.
