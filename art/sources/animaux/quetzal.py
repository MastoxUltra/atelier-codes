"""Le quetzal en peluche de velours ras, refait le 19/10 d'après son modèle 3D (references_3d/quetzal, CC-BY : des vues
seulement, rien n'en est importé) et les photos de Commons (photos/, CC0). L'ancien dessin (refusé : « corps en chaussette,
gilet rouge plaqué ») est dans le scratchpad de l'agent (quetzal_avant_1019.py). Construit comme le perroquet gardé par
l'auteur : un œuf penché, un cou court et plein, une tête ronde, les ailes couchées sur les flancs, la queue en plumes plates.

Les 5 traits de l'espèce : 1. un oiseau trapu, droit comme un piquet, turquoise profond (registre : jamais vert) ;
2. le ventre cramoisi, du bas du poitrail jusque sous la queue, fondu dans le turquoise (pas de gilet cousu) ; 3. la
tête ronde coiffée d'une crête en brosse arrondie, de la base du bec à la nuque, le petit bec jaune à moitié dans les
plumes, de grands yeux noirs ; 4. les ailes noires sous de longues plumes turquoise qui retombent dessus ; 5. LA TRAÎNE :
deux très longues plumes (plus de deux fois le corps) qui tombent du croupion et filent au sol derrière lui, deux plus
courtes à côté, le dessous de la queue blanc.

    python quetzal.py        fabrique la fiche art/apercus/animaux/quetzal.png (velours ras, palier 3)
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

TURQUOISE = np.array(M.hexa("#1f9ad8"))       # la dominante (registre) : turquoise profond, qui penche vers le bleu
CRETE = np.array(M.hexa("#29a6df"))           # la crête, un cran plus vive
NUIT = np.array(M.hexa("#1560b8"))            # le dos, le bord et le bout des longues plumes
CRAMOISI = np.array(M.hexa("#e8244a"))        # l'accent : le ventre
NOIR_AILE = np.array(M.hexa("#1d2434"))       # les grandes plumes de l'aile, presque noires
BLANC = np.array(M.hexa("#fff8f0"))           # le dessous de la queue
BEC = M.hexa("#ffd22a")                       # le bec
PATTE = M.hexa("#5e5048")                     # les pattes, brun gris sombre

# ---- les mesures (proportions du modèle de référence et des photos : droit, trapu, la tête grosse, la traîne deux fois
#      et demie le corps) ----
BASE = Vector((0.0, 0.050, 0.100))            # le bas du corps
PENTE = 20.0                                  # presque droit (le vrai, perché : 15 à 25° de la verticale)
LONG = 0.300                                  # la longueur du corps
TETE = Vector((0.0, -0.062, 0.412))
TETE_R = (0.072, 0.074, 0.070)                # une tête de peluche, un peu grosse
LACET = 14.0                                  # la tête un peu tournée vers nous


def plume_suivie(chemin, normales, large, paliers, plat=0.28, cotes=16, pas=8, bord=None):
    """Une plume plate couchée le long d'un chemin, sa face à plat contre la normale donnée à chaque point (elle tombe
    du croupion puis se couche au sol sans se vriller). paliers = [(fraction, couleur), ...] le long de la plume ; bord :
    une couleur pour ses deux bords (le liseré bleu nuit des longues plumes du vrai)."""
    p = A.courbe(chemin, pas)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    s_ctrl = fait[[i * pas for i in range(len(chemin))]]
    N = np.asarray(normales, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-9)
        n = np.stack([np.interp(s, s_ctrl, N[:, k]) for k in range(3)], axis=-1)
        x = np.cross(n, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.60 * large, 0.03 * L), (0.95 * large, 0.16 * L), (large, 0.45 * L), (0.86 * large, 0.75 * L),
                     (0.50 * large, 0.93 * L), (0, L)], 5)
    m = A.tour(prof, cotes).etire(1.0, plat, 1.0)
    f = np.clip(m.v[:, 2] / L, 0.0, 1.0)
    tq = np.zeros((len(f), 3))
    reste = np.ones(len(f), bool)
    for fr, col in paliers:
        ici = reste & (f <= fr)
        tq[ici] = col
        reste &= ~ici
    tq[reste] = paliers[-1][1]
    if bord is not None:
        rx = np.abs(m.v[:, 0]) / np.maximum(np.hypot(m.v[:, 0], m.v[:, 1] / plat), 1e-9)
        b = K.lisse((rx - 0.80) / 0.15)[:, None]
        tq = tq * (1 - b) + np.asarray(bord, float)[None, :] * b
    m.teinte = tq
    return m.sculpte(couche)


def construire():
    a = K.Animal("quetzal")
    a.taille = 1.00                           # traîne comprise
    a.fusion_a_part = ("aile", "queue")       # les ailes et la traîne restent des pièces : on les lit (pas de boudin gonflé)

    # ----- le corps : un œuf trapu presque droit, le poitrail bombé ; le cramoisi du ventre peint sur la peau, sa limite
    #       en biais (haute devant, basse sur les flancs) et un peu festonnée, comme des plumes -----
    T = A.repere(BASE, (PENTE, 0, 0))
    pc = A.profil([(0, 0.0), (0.058, 0.012), (0.090, 0.052), (0.104, 0.118), (0.101, 0.178), (0.088, 0.230), (0.066, 0.268),
                   (0, LONG)], 6)
    corps = A.tour(pc, 56)

    def galbe(v):
        s = v.copy()
        f = np.clip(v[:, 2] / LONG, 0, 1)
        s[:, 1] = np.where(v[:, 1] < 0, v[:, 1] * (1.0 + 0.14 * np.sin(np.pi * f)), v[:, 1] * 0.86)    # le poitrail devant
        s[:, 0] *= 0.96
        return s
    corps.sculpte(galbe)
    f = np.clip(corps.v[:, 2] / LONG, 0, 1)
    ang = np.arctan2(corps.v[:, 0], -corps.v[:, 1])                   # 0 : le devant ; ±pi : le dos
    devant = np.cos(np.clip(np.abs(ang), 0, math.pi))                # 1 devant, 0 sur le flanc, -1 au dos
    limite = 0.40 + 0.20 * devant + 0.025 * np.sin(7.0 * ang)        # haute devant, basse sur les flancs, festonnée
    rouge = K.lisse((limite - f) / 0.06) * K.lisse((devant + 0.55) / 0.40)
    dos = K.lisse((-devant - 0.55) / 0.35) * K.lisse((f - 0.15) / 0.2)
    tc = TURQUOISE[None, :] * (1 - dos[:, None]) + NUIT[None, :] * (0.55 * dos[:, None]) + TURQUOISE[None, :] * (0.45 * dos[:, None])
    corps.teinte = tc * (1 - rouge[:, None]) + CRAMOISI[None, :] * rouge[:, None]
    a.piece("corps", corps, None, mat=T)
    haut = Vector(T @ Vector((0, 0, 0.250)))

    # ----- le cou, court et plein : la tête TIENT au corps -----
    RT = A.repere(TETE, (-4, 0, LACET))
    cou = O.tube_r([tuple(haut + Vector((0, 0.020, -0.040))), tuple(haut + Vector((0, -0.006, 0.026))),
                    tuple(RT @ Vector((0, 0.012, -0.024)))], [0.080, 0.070, 0.060], 22)
    a.piece("cou", O.teinte(cou, tuple(TURQUOISE)), None)

    # ----- la tête : ronde ; la crête en brosse arrondie, aplatie sur les côtés, de la base du bec jusqu'à la nuque -----
    tete = A.boule(1.0, 56, 28)
    tete.sculpte(lambda v: K.bosse(v, (0, -0.3, 0.9), 0.05, 0.35))
    a.piece("tete", O.teinte(tete.etire(*TETE_R), tuple(TURQUOISE)), None, mat=RT)
    crete = A.boule(1.0, 40, 20)

    def brosse(v):
        s = K.bosse(v, (0, 0, 1), 0.10, 0.5)
        s = s * [0.027, 0.070, 0.046]
        s[:, 2] -= 0.18 * np.clip(-s[:, 1], 0, None)                               # l'avant plonge vers le bec
        return s
    crete.sculpte(brosse)
    a.piece("tete_crete", O.teinte(crete, tuple(CRETE)), None, mat=RT @ A.repere((0, -0.012, 0.050), (8, 0, 0)))
    a.tete = RT @ Vector((0.0, -0.090, -0.010))

    # le petit bec jaune, court, à moitié dans les plumes du front
    R3 = RT.to_3x3()
    B = A.cadre(RT @ Vector((0, -0.058, -0.014)), R3 @ Vector((0, -0.97, -0.16)), R3 @ Vector((0, 0, 1)))
    bec = A.tour(A.profil([(0, 0), (0.021, 0.005), (0.019, 0.020), (0.012, 0.034), (0.005, 0.044), (0, 0.048)], 5), 28)
    a.piece("bec", bec.etire(0.95, 0.74, 1.0), BEC, mat=B, poil=False)
    O.paire_yeux(a, "tete", TETE, (0.62, -0.70, 0.18), 0.0175, decolle=0.003, R=RT)

    # ----- les ailes repliées sur les flancs, turquoise à l'épaule, noires au bout ; de longues plumes turquoise qui
    #       retombent par-dessus (le geste du vrai) ; les pointes jusqu'à la racine de la queue -----
    for nom, c in (("G", 1), ("D", -1)):
        pts = []
        for f_, d_ in ((0.84, (c * 1.0, -0.10, 0.10)), (0.64, (c * 1.0, 0.25, 0.0)), (0.44, (c * 1.0, 0.50, -0.05)), (0.24, (c * 1.0, 0.80, -0.10))):
            p_, n_ = a.surface("corps", T @ Vector((0.0, 0.0, f_ * LONG)), Vector(d_))
            pts.append(tuple(p_ + n_ * 0.010))
        pts.append((c * 0.040, 0.165, 0.120))
        pts.append((c * 0.024, 0.205, 0.090))
        fil = K.Fil(pts, flanc=(c, 0.0, 0.0))
        LA = fil.long
        aile = A.tour(A.profil([(0, 0), (0.046, 0.08 * LA), (0.068, 0.26 * LA), (0.066, 0.50 * LA), (0.050, 0.72 * LA), (0.028, 0.90 * LA),
                                (0, LA)], 6), 36)
        fa = aile.v[:, 2] / LA
        g = K.lisse((fa - 0.36) / 0.10)[:, None]
        aile.teinte = TURQUOISE[None, :] * (1 - g) + NOIR_AILE[None, :] * g
        a.piece("aile_" + nom, aile.etire(0.40, 1.0, 1.0).sculpte(fil.couche), None)
        # les plumes de l'épaule qui retombent sur le noir : posées sur l'aile, côte à côte, de plus en plus longues
        for k in range(4):
            s0 = LA * (0.10 + 0.05 * k)
            centre, avant, nuque = (np.asarray(x) for x in fil.cadre(s0))
            dehors = np.array((c, 0.0, 0.0))
            p0, n0 = a.surface("aile_" + nom, Vector(tuple(centre)), Vector(tuple(dehors + 0.25 * nuque)))
            p0 = np.array(p0) - np.array(n0) * 0.003
            n0 = np.array(n0)
            long_ = 0.11 + 0.025 * k
            bas_ = np.array((0.0, 0.0, -1.0))
            arr = np.array((0.0, 1.0, 0.0))
            chemin = [p0, p0 + long_ * (0.45 * bas_ + 0.30 * arr) + n0 * 0.006, p0 + long_ * (0.80 * bas_ + 0.55 * arr) + n0 * 0.004]
            pl = plume_suivie(chemin, [n0, n0, n0], 0.016, [(0.70, TURQUOISE), (1.0, NUIT)], 0.30, 12, 6)
            a.piece("aile_plume_%s%d" % (nom, k), pl, None)

    # ----- la queue : le dessous blanc, court ; LA TRAÎNE : deux très longues plumes qui tombent du croupion et filent au
    #       sol derrière lui en ondulant, deux plus courtes à côté ; turquoise, le bord et le bout bleu nuit -----
    haut_ = np.array((0.0, 0.0, 1.0))
    a.piece("queue_blanche", plume_suivie([(0.0, 0.085, 0.118), (0.0, 0.160, 0.072), (0.0, 0.215, 0.040)],
                                          [(0.0, 0.6, 0.8), (0.0, 0.7, 0.7), (0.0, 0.8, 0.6)], 0.040, [(1.0, BLANC)], 0.30), None)
    for nom, c, x0, long_, onde_ in (("G", 1, 0.010, 1.00, 0.030), ("D", -1, 0.010, 0.96, 0.034), ("cote_G", 1, 0.030, 0.62, 0.020),
                                      ("cote_D", -1, 0.030, 0.60, 0.022)):
        y_sol = 0.300                                                  # là où elle touche le sol
        y_fin = y_sol + 0.560 * long_
        chemin = [(c * x0, 0.085, 0.150), (c * (x0 + 0.004), 0.170, 0.122), (c * (x0 + 0.010), 0.236, 0.066), (c * (x0 + 0.016), y_sol, 0.016)]
        normales = [(0.0, 0.30, 0.95), (0.0, 0.55, 0.84), (0.0, 0.62, 0.78), (0.0, 0.15, 0.99)]
        for k in range(1, 4):
            q = k / 3.0
            chemin.append((c * (x0 + 0.016 + 0.040 * q) + onde_ * math.sin(math.pi * 1.5 * q) * c, y_sol + (y_fin - y_sol) * q, 0.014))
            normales.append(tuple(haut_))
        large = 0.046 if "cote" not in nom else 0.034
        a.piece("queue_" + nom, plume_suivie(chemin, normales, large, [(0.62, TURQUOISE), (1.0, NUIT)], 0.26, 16, 8, bord=NUIT), None)

    # ----- les pattes : courtes, presque cachées sous le ventre rouge ; deux doigts devant, deux derrière -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("culotte_" + nom, A.boule(1.0, 28, 14).etire(0.040, 0.048, 0.050), tuple(CRAMOISI), pos=(c * 0.046, 0.020, 0.112))
        ch = [(c * 0.044, 0.012, 0.092), (c * 0.046, 0.002, 0.052), (c * 0.046, -0.006, 0.020)]
        a.piece("patte_" + nom, A.tube(A.courbe(ch, 5), 0.0130, 12), PATTE, poil=False)
        doigts = None
        for ang, long_ in ((-20, 0.038), (20, 0.038), (160, 0.028), (200, 0.028)):
            d = A.boule(1.0, 14, 7).etire(0.0085, long_ * 0.5, 0.0085).pose((0, -long_ * 0.5, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("orteils_" + nom, doigts, PATTE, pos=(c * 0.046, -0.006, 0.009), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("quetzal", styles.style_de("quetzal"), sys.modules[__name__]), "Quetzal")
