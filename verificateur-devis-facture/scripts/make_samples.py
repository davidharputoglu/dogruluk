#!/usr/bin/env python3
"""Exemples de donnees de test : liste de prix Point.P + facture avec 1 ecart
+ 1 article absent + chantier. A remplacer par tes vrais fichiers des que tu
les deposes dans verificateur-devis-facture/."""
import csv
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLES = os.path.join(HERE, "..", "samples")
os.makedirs(SAMPLES, exist_ok=True)

prices = [
    ["Code article", "Designation", "Unite", "Prix HT"],
    ["100234567", "Ciment CPA 45 - sac 35kg", "U", "6,20"],
    ["100111222", "Brique pleine 8T 22x10x5", "U", "0,95"],
    ["100987654", "Parpaing 20x20x50 creux", "U", "1,85"],
    ["100555666", "Mortier batard 35 kg", "U", "5,10"],
]

invoice = [
    ["Reference", "Designation", "Unite", "Quantite", "PU HT"],
    ["100234567", "CIMENT CPA 45 SAC 35KG", "U", "150", "6,20"],      # conforme
    ["100987654", "Parpaing 20x20x50 creux", "U", "400", "2,10"],     # ecart: (2,10-1,85)*400 = 100
    ["100111222", "Brique pleine 8T 22x10x5", "U", "1000", "0,95"],   # conforme
    ["777000888", "Treillis soudé ST25 6m", "U", "20", "34,90"],      # prix absent
]

with open(os.path.join(SAMPLES, "liste_prix_pointp_exemple.csv"), "w", newline="", encoding="utf-8-sig") as f:
    csv.writer(f, delimiter=";").writerows(prices)
with open(os.path.join(SAMPLES, "facture_pointp_exemple.csv"), "w", newline="", encoding="utf-8-sig") as f:
    csv.writer(f, delimiter=";").writerows(invoice)
print("Ecrit :", SAMPLES)
