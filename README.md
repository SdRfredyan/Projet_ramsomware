# 🛡️ Projet Ransomware Pédagogique en Python

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
