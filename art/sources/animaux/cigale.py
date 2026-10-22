"""La cigale en peluche : une grosse tête carrée bronze doré clair, deux yeux à fleur de crâne, un thorax bossu, et
sur le dos, deux grandes ailes fumées, nervurées comme des vitraux, qui retombent en toit ; le ventre rayé, un peu
creux : c'est une caisse de résonance. Plantée sur ses pattes courtes, la tête levée, le ventre gonflé : elle a
chanté tout l'été, elle y revient, et elle ne s'est jamais demandé si on l'aimait.

    python cigale.py        fabrique la fiche art/apercus/animaux/cigale.png (style du palier : A, cousu main)
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

BRONZE = np.array(M.hexa("#d6b068"))          # la dominante (registre : bronze doré clair)
RAIE = np.array(M.hexa("#8a6a30"))            # les rayures du ventre
FUMEE = M.hexa("#e6dcc0")                     # les ailes fumées
NERVURE = M.hexa("#3e3322")
OEIL = M.hexa("#8a2a22")
PATTE = np.array(M.hexa("#a88848"))
FIL = M.hexa("#4a3a20")


def construire():
    a = K.Animal("cigale")
    a.taille = 0.34

    # ----- le corps : une tête large et carrée, un thorax bossu, un abdomen à rayures sombres qui s'effile -----
    tete = A.boule(1.0, 36, 18).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.085, 0.050, 0.060)
    tete.teinte = np.tile(BRONZE, (len(tete.v), 1))
    a.piece("tete", tete, None, pos=(0.0, -0.150, 0.135))
    thorax = A.boule(1.0, 36, 18).etire(0.080, 0.085, 0.080)
    thorax.teinte = np.tile(BRONZE * 0.96, (len(thorax.v), 1))
    a.piece("thorax", thorax, None, pos=(0.0, -0.070, 0.135))
    pc = A.profil([(0, 0.0), (0.050, 0.014), (0.068, 0.070), (0.058, 0.160), (0.036, 0.230), (0.012, 0.275), (0, 0.290)], 5)
    abd = A.tour(pc, 28)
    abd.teinte = np.where((np.sin(abd.v[:, 2] * 62) > 0.4)[:, None], RAIE, BRONZE)
    a.piece("abdomen", abd, None, mat=A.cadre(Vector((0.0, -0.020, 0.130)), (0.0, 1.0, -0.20), (0, 0, 1)))

    # ----- le visage : deux gros yeux saillants sur les côtés, deux petits boutons devant, les antennes -----
    H = Vector((0.0, -0.150, 0.135))
    for nom, c in (("G", 1), ("D", -1)):
        o = A.boule(1.0, 20, 10).etire(0.030, 0.034, 0.034)
        a.piece("globe_" + nom, O.teinte(o, np.array(OEIL)), None, pos=(c * 0.092, -0.158, 0.145), poil=False)
    for nom, c in (("G", 1), ("D", -1)):                            # DEUX yeux : une pupille vivante sur chaque globe (plus de boutons en plus)
        pg, ng = a.surface("globe_" + nom, Vector((c * 0.092, -0.158, 0.145)), Vector((c * 0.40, -0.90, 0.25)))
        a.oeil("oeil_" + nom, pg + ng * 0.002, ng, 0.0200)
    for nom, c in (("G", 1), ("D", -1)):
        ant = O.tube_r([(c * 0.020, -0.190, 0.178), (c * 0.036, -0.230, 0.210)], [0.0050, 0.0040], 8)
        a.piece("antenne_" + nom, O.teinte(ant, RAIE), None, poil=False)
    a.tete = H + Vector((0.0, -0.06, 0.0))

    # ----- les ailes : deux grandes lames fumées, nervurées, qui retombent en toit sur le dos et dépassent l'abdomen -----
    contour = [(0.0, 0.0), (0.04, -0.012), (0.09, -0.016), (0.13, 0.060), (0.145, 0.230), (0.125, 0.420), (0.060, 0.500), (0.00, 0.160)]      # longues et étroites : plus longues que le corps, comme le modèle de référence
    def lift(x, y):
        return (x, y, 3.60 * x * x + 0.60 * (y - 0.15) ** 2)
    for nom, c in (("G", 1), ("D", -1)):
        rep = A.repere((c * 0.034, -0.062, 0.210), (0, c * 34, 0))
        # l'aile est un VITRAIL : le bord et les nervures seulement, les cellules restent vides (on voit au travers : elle est
        # transparente, plus un carton blanc)
        def tube_ligne(points, rayon, couleur):
            pts = A.courbe([tuple(rep @ Vector(lift(c * px, py))) for px, py in points], 4)
            m_ = O.tube_r([tuple(p_) for p_ in pts], [rayon, rayon], 8)
            return O.teinte(m_, couleur)
        cont = [(x_, y_) for x_, y_ in contour] + [contour[0]]
        aile = tube_ligne(cont, 0.0050, np.asarray(NERVURE) * 1.4)
        for off in (0.02, 0.045, 0.07, 0.095, 0.120):
            aile = aile + tube_ligne([(off, 0.01), (off + 0.02, 0.16), (off + 0.025, 0.32), (off + 0.005, 0.46)], 0.0028, np.asarray(NERVURE))
        for y_ in (0.10, 0.20, 0.30, 0.40):
            aile = aile + tube_ligne([(0.010, y_), (0.055, y_ + 0.008), (0.100, y_ - 0.005), (0.140, y_ + 0.006)], 0.0024, np.asarray(NERVURE))
        a.piece("aile_" + nom, aile, None, poil=False)

    # ----- les pattes : deux de chaque côté, courtes ; les antérieures plus fortes -----
    for k, (y, ep) in enumerate(((-0.100, 0.018), (-0.040, 0.014), (0.010, 0.012))):
        for nom, c in (("G", 1), ("D", -1)):
            p = O.tube_r([(c * 0.050, y, 0.105), (c * 0.115, y - 0.015, 0.090), (c * 0.140, y + 0.010, 0.007)], [ep, ep * 0.85, ep * 0.65], 8)
            a.piece("patte_%s%d" % (nom, k), O.teinte(p, PATTE), None, poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "membres")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("cigale", styles.style_de("cigale"), sys.modules[__name__]), "Cigale")
