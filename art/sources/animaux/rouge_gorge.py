"""Le rouge-gorge en peluche : une boule de plumes brun gris, le plastron orange rouge vif qui lui monte du ventre
jusqu'aux joues comme un tablier, de grands yeux noirs bien ronds. Il se tient droit sur ses pattes grêles, le poitrail en
avant, la queue relevée, la tête un peu penchée : il est chez lui, ici, c'est son jardin, et il aime qu'on le sache.

    python rouge_gorge.py        fabrique la fiche art/apercus/animaux/rouge_gorge.png (style du palier : A, cousu main)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import peluche as K
import outils_a as O

BRUN = np.array(M.hexa("#9a8670"))            # la dominante (registre : dos brun gris)
ORANGE = np.array(M.hexa("#f2561c"))          # l'accent : le plastron
CLAIR = np.array(M.hexa("#e8dccc"))           # le ventre bas
GRIS = np.array(M.hexa("#c6c0b6"))            # le lisere gris autour du plastron
BEC = M.hexa("#3a2f2a")
PATTE = M.hexa("#7a5a4a")


def peint_corps(m, t):
    """Le plastron orange sur la poitrine et la gorge, le liseré gris au bord, le ventre bas clair."""
    ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
    z = m.v[:, 2]
    L = float(z.max())
    devant = z / L
    t = t.copy()
    t[(ang > 1.45) & (devant > 0.50)] = GRIS
    t[(ang > 1.70) & (devant > 0.56)] = ORANGE
    return t


def peint_tete(m, t):
    """La face orange : le devant bas de la tête, cerné d'un liseré gris."""
    u = m.v / np.maximum(np.linalg.norm(m.v, axis=1, keepdims=True), 1e-9)
    t = t.copy()
    t[(u[:, 1] < -0.10) & (u[:, 2] < 0.45)] = GRIS
    t[(u[:, 1] < -0.25) & (u[:, 2] < 0.30)] = ORANGE
    return t


def construire():
    a = K.Animal("rouge_gorge")
    a.taille = 0.30

    # (19/10, d'après les vues de la référence : une boule de plumes inclinée, la tête enfoncée dans le poitrail, SANS cou ;
    #  l'aile couchée contre le flanc, qui s'effile ; une longue queue qui prolonge le dos ; de hautes pattes grêles)
    r = O.oiseau(a, dos=BRUN, ventre=CLAIR, tete=BRUN, aile=BRUN * 0.88, queue=BRUN * 0.82, bec=BEC, patte=PATTE, long=0.25, ray=0.100,
                 incline=38.0, z0=0.120, tete_r=(0.066, 0.068, 0.064), tete_pos=(0.0, -0.038, 0.006), bec_long=0.042, bec_ray=0.0112,
                 aile_dim=(0.020, 0.058, 0.150), aile_pos=(-0.014, 0.014, -0.010), aile_pointue=True,
                 queue_dim=(0.032, 0.105, 0.011), queue_haut=-38.0,
                 patte_long=0.125, patte_ray=0.0070, oeil_r=0.0165, oeil_dir=(0.70, -0.60, 0.20), coupe_dos=1.1, bec_suit=True, cou_ray=0.0,
                 peint_corps=peint_corps, peint_tete=peint_tete)
    H, T, haut = r["H"], r["T"], r["haut"]

    # (le plastron et la face sont peints sur le corps et la tête : plus de boules orange posées dessus)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("rouge_gorge", styles.style_de("rouge_gorge"), sys.modules[__name__]), "Rouge-gorge")
