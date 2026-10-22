"""Le faucon en peluche : roux brique moucheté de brun, la tête gris bleu coiffée d'une moustache noire sous chaque
œil, la poitrine mouchetée, un bec crochu court et sombre sur une cire jaune. Droit sur ses serres, les ailes en lame
repliées plus longues que la queue, il regarde par-dessus l'épaule avec un air de ne pas aimer ce qu'il voit :
il n'y a pas de quoi, c'est un faucon.

    python faucon.py        fabrique la fiche art/apercus/animaux/faucon.png (style du palier : C, velours ras)
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

BRIQUE = np.array(M.hexa("#b5623e"))          # la dominante (registre : roux brique moucheté)
TACHE = np.array(M.hexa("#6a3a28"))
CLAIR = np.array(M.hexa("#e8cfb0"))           # le ventre, moucheté
GRISBLEU = np.array(M.hexa("#7f8c9a"))        # la tête
NOIR = M.hexa("#1d1a1c")                      # la moustache
JAUNE = M.hexa("#f0c030")                     # la cire, les pattes
BEC = M.hexa("#cfc8b4")                       # le bec : corne claire, bien visible sur la tête bleu-gris


def peint_tete(m, t):
    """La moustache du faucon : une seule goutte sombre PEINTE sous chaque œil, jamais des poils posés au bec ni un masque autour de l'œil."""
    u = m.v / np.maximum(np.linalg.norm(m.v, axis=1, keepdims=True), 1e-9)
    t = t.copy()
    for c in (1, -1):
        d = np.array([c * 0.40, -0.70, -0.60]); d /= np.linalg.norm(d)
        t[(u @ d) > 0.950] = np.array(NOIR)
    return t


def peint_corps(m, t):
    """Les mouchetures PEINTES (19/10 : les taches posées se lisaient comme des trous) : des barres sombres sur le poitrail clair,
    des écailles brunes sur le dos."""
    ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))             # 0 : le dos ; pi : le ventre
    z = m.v[:, 2]
    t = t.copy()
    t[(ang > 1.95) & (z > 0.14) & (np.sin(z * 88.0 + ang * 3.0) > 0.45)] = TACHE * 0.75 + CLAIR * 0.25
    t[(ang < 1.05) & (np.sin(z * 64.0 + ang * 9.0) > 0.82)] = TACHE
    return t


def construire():
    a = K.Animal("faucon")
    a.taille = 0.58

    # (19/10, d'après les vues de la référence : un rapace DROIT et élancé, la tête petite sur de larges épaules, les ailes longues
    #  et pointues couchées le long du dos, la queue longue dans le prolongement du corps, le bec court et crochu)
    r = O.oiseau(a, dos=BRIQUE, ventre=CLAIR, tete=GRISBLEU, aile=BRIQUE * 0.90, queue=BRIQUE * 0.80, bec=BEC, patte=JAUNE, long=0.40,
                 ray=0.098, incline=24.0, z0=0.112, tete_r=(0.058, 0.066, 0.056), tete_pos=(0.0, -0.052, 0.030), bec_long=0.050,
                 bec_ray=0.0245, bec_baisse=-0.35, aile_dim=(0.022, 0.066, 0.235), aile_pos=(-0.012, 0.024, -0.040),
                 queue_dim=(0.042, 0.012, 0.100), queue_m=((0.0, 0.100, 0.108), (24, 0, 0)), patte_long=0.100, patte_ray=0.0125,
                 oeil_r=0.0205, oeil_dir=(0.36, -0.90, 0.22), bout_aile=BRIQUE * 0.55, coupe_dos=1.25, tete_rot=(-6, 0, 0), cou_ray=0.052,
                 aile_pointue=True, peint_corps=peint_corps, peint_tete=peint_tete)
    H, T, haut = r["H"], r["T"], r["haut"]

    # le bec crochu : le bout du bec se recourbe vers le bas en un crochet pointu, sur une cire jaune
    a.piece("crochet", O.couche(O.teinte(O.pointe(0.040, 0.0140, 8), np.array(M.hexa("#4a4650"))), A.cadre(H + Vector((0.0, -0.097, -0.014)), Vector((0.0, -0.10, -1.0)), (0, 1, 0))), None, poil=False)
    cire = A.boule(1.0, 16, 8).etire(0.016, 0.012, 0.011)
    a.piece("cire", cire, JAUNE, pos=tuple(H + Vector((0.0, -0.062, -0.004))), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("faucon", styles.style_de("faucon"), sys.modules[__name__]), "Faucon")
