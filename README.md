# 🛡️ Projet Ransomware Pédagogique en Python

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Security](https://img.shields.io/badge/Security-Offensive-red.svg)](#)
[![Educational](https://img.shields.io/badge/Purpose-Educational-green.svg)](#)

Ce projet est réalisé dans le cadre du module **"Malware et sécurité offensive en Python"**. Il simule le comportement d'un ransomware moderne à des fins éducatives.

> [!CAUTION]
> **AVERTISSEMENT :** Ce code est destiné à un usage strictement pédagogique en environnement contrôlé. **Ne l'exécutez jamais sur votre machine physique**. Utilisez exclusivement une Machine Virtuelle (VM) isolée.

---

## 📋 Table des Matières
1. [Contexte et Objectifs](#-contexte-et-objectifs)
2. [Fonctionnement Technique](#-fonctionnement-technique)
3. [Installation](#-installation)
4. [Utilisation](#-utilisation)
5. [Documentation des Commandes](#-documentation-des-commandes)
6. [Analyses et Faiblesses](#-analyses-et-faiblesses)

---

## 🎯 Contexte et Objectifs

L'objectif principal est de comprendre l'architecture interne d'un malware et les vecteurs de communication entre un client infecté et son serveur de contrôle (C2).

**Compétences travaillées :**
* **Système :** Manipulation récursive de fichiers et répertoires.
* **Cryptographie :** Implémentation du chiffrement XOR symétrique.
* **Réseau :** Développement d'un protocole client/serveur TCP multi-clients.
* **Sécurité :** Analyse des traces (logs) et gestion d'authentification par token.

---

## ⚙️ Fonctionnement Technique

### Architecture
Le projet repose sur une architecture **Client/Serveur (C2)** :
1.  **Le Client (`client.py`)** : Génère une clé unique, chiffre un dossier spécifique et exfiltre les informations vers le serveur.
2.  **Le Serveur (`server.py`)** : Centralise les clés de déchiffrement et envoie des commandes à distance via une console interactive.

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
