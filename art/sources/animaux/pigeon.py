"""Le pigeon en peluche : un gros ballon gris ardoise clair, le cou irisé de reflets violets, qui se promène en
dodelinant, le poitrail bombé en avant, la tête qui précède le corps. Les pattes roses, un petit œil orange rond,
deux bandes sombres sur les ailes : il a l'air de chercher des miettes, et il en trouve toujours.

    python pigeon.py        fabrique la fiche art/apercus/animaux/pigeon.png (style du palier : A, cousu main)
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

ARDOISE = np.array(M.hexa("#9aa5b4"))         # la dominante (registre : gris ardoise clair)
CLAIR = np.array(M.hexa("#bcc4cf"))           # le ventre
VIOLET = np.array(M.hexa("#8a5fb0"))          # les reflets du cou
VERT = np.array(M.hexa("#7a8fc2"))            # le reflet bleuté (jamais de vert franc)
SOMBRE = np.array(M.hexa("#5a6272"))          # les bandes des ailes
BEC = M.hexa("#403840")
CIRE = M.hexa("#e8e2da")
ROSE = M.hexa("#e58a98")                      # les pattes
OEIL = M.hexa("#f08a2a")


def construire():
    a = K.Animal("pigeon")
    a.taille = 0.44

    # (19/10, d'après les vues de la référence, un vrai biset : un corps rond COUCHÉ, presque horizontal, la petite tête ronde en avant sur un
    #  cou court irisé, l'aile repliée à plat sur le flanc avec deux barres sombres, la queue qui prolonge le corps, les pattes basses)
    def barres(al, f, tl):
        tl = tl.copy()
        for centre in (-0.12, -0.46):
            tl[np.abs(f - centre) < 0.075] = SOMBRE
        return tl

    r = O.oiseau(a, dos=ARDOISE, ventre=CLAIR, tete=ARDOISE, aile=ARDOISE * 0.98, queue=SOMBRE, bec=BEC, patte=ROSE, long=0.34, ray=0.112,
                 incline=58.0, z0=0.112, tete_r=(0.060, 0.064, 0.058), tete_pos=(0.0, -0.062, 0.030), bec_long=0.050, bec_ray=0.0125, bec_suit=True, cou_ray=0.052,
                 aile_dim=(0.020, 0.062, 0.185), aile_pos=(-0.014, 0.022, -0.014), aile_pointue=True, bout_aile=SOMBRE, peint_aile=barres,
                 queue_dim=(0.048, 0.115, 0.012), queue_m=((0.0, 0.158, 0.118), (-14, 0, 0)),
                 patte_long=0.085, patte_ray=0.0100, oeil_r=0.0150, oeil_dir=(0.76, -0.52, 0.18), coupe_dos=1.25)
    H, T, haut = r["H"], r["T"], r["haut"]

    # ----- le cou irisé : un collier de reflets violets et bleutés qui entoure la base de la tête ; la cire blanche à la base du bec -----
    for k, (c, h) in enumerate(((VIOLET, 0.0), (VERT, -0.022))):
        col = A.tore(0.048 - 0.006 * k, 0.019, 28, 8)
        a.piece("collier_%d" % k, O.teinte(col, c), None, pos=tuple(haut + Vector((0.0, -0.046, 0.020 + h))), rot=(60, 0, 0))
    cire = A.boule(1.0, 16, 8).etire(0.016, 0.014, 0.012)
    a.piece("cire", cire, CIRE, pos=tuple(H + Vector((0.0, -0.058, -0.002))), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pigeon", styles.style_de("pigeon"), sys.modules[__name__]), "Pigeon")
