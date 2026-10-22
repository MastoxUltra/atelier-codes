"""La pie en peluche (4e dessin, 18/10, Art : d'après les vues d'une vraie, CC-BY, rien d'importé) : noir et blanc
tranchés. La tête, le cou, la poitrine et le dos noirs, le ventre et les flancs blancs, une longue bande blanche sur
l'épaule ; un bec fort, noir, droit ; et la queue : UNE longue queue étagée, aussi longue que le corps, noire à reflets
bleus, tenue un peu relevée derrière elle. Elle marche dans l'herbe, l'œil rond qui a déjà repéré ce qui brille chez vous.

    python pie.py        fabrique la fiche art/apercus/animaux/pie.png (style du palier : A, cousu main)

Les 5 traits de l'espèce : 1. noir et blanc tranchés (ventre et flancs blancs) ; 2. la bande blanche de l'épaule ; 3. la
longue queue étagée à reflets bleus ; 4. le bec fort et noir ; 5. une silhouette de corvidé, la queue relevée.
(refusés : « une boule à tête ronde », « le corps toujours une boule » le 15/10 ; au contrôle du 16/10 : « queue en deux
lames écartées, tête fondue sans œil visible ». Ici : un œil cerclé de gris sur la tête noire, une seule queue serrée.)
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

NOIR = np.array(M.hexa("#25252c"))            # la dominante (registre : noir et blanc tranchés)
BLANC = np.array(M.hexa("#fbfaf4"))
BLEU = np.array(M.hexa("#2b4a8c"))            # les reflets bleus de la queue et des ailes
SARCELLE = np.array(M.hexa("#2a6276"))        # le bout de la queue, bleu-vert sombre (jamais un vert franc)
CERNE = np.array(M.hexa("#6a6e7c"))           # le tour de l'œil, gris : l'œil noir se voit sur la tête noire
BEC = M.hexa("#1a181c")
PATTE = np.array(M.hexa("#2a282e"))

CROUPE = (0.0, 0.090, 0.110)                  # le centre de la croupe (le corps couché part de là vers l'avant)
LC = 0.220
PENTE = 24.0
TETE = Vector((0.0, -0.130, 0.258))
LACET = 18.0


def construire():
    a = K.Animal("pie")
    a.taille = 1.00                            # la queue dépasse le corps : c'est ce qui fait la taille
    a.fusion_a_part = ("aile", "queue")        # les ailes et les plumes de la queue restent des pièces (on les lit)

    # ----- le corps : un fuseau couché, la poitrine relevée ; le dos et le bavoir noirs, le ventre et les flancs blancs -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))              # 0 : le dos ; pi : le ventre
        fr = m.v[:, 2] / L                                          # 0 : la croupe ; 1 : la poitrine
        t_ = np.tile(NOIR, (len(ang), 1))
        t_[(ang > 1.30) & (fr > 0.16) & (fr < 0.74)] = BLANC        # le ventre et les flancs, tranchés net
        return t_
    rayon = O.interp([(0.0, 0.0), (0.06, 0.030), (0.28, 0.062), (0.56, 0.074), (0.80, 0.070), (0.94, 0.050), (1.0, 0.020)])
    T = O.corps_h(a, "corps", CROUPE, LC, rayon, peint, None, cotes=56, pitch=PENTE)

    # ----- le cou et la tête noirs ; l'œil noir cerclé de gris ; le bec fort, noir, presque droit -----
    a.piece("cou", O.teinte(O.tube_r([(0.0, -0.080, 0.196), (0.0, -0.104, 0.226), (0.0, -0.122, 0.248)], [0.064, 0.058, 0.053], 22), NOIR), None)
    RT = A.repere(TETE, (-4, 0, LACET))
    tete = A.boule(1.0, 48, 24)
    tete.teinte = np.tile(NOIR, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.050, 0.056, 0.048), None, mat=RT)
    OEIL = (0.68, -0.64, 0.26)
    for nom, c in (("G", 1), ("D", -1)):
        a.rustine("cerne_" + nom, "tete", TETE, RT.to_3x3() @ Vector((c * OEIL[0], OEIL[1], OEIL[2])), 0.36, tuple(CERNE), 0.003, 0)
    O.paire_yeux(a, "tete", TETE, OEIL, 0.0140, decolle=0.004, R=RT)
    a.tete = RT @ Vector((0.0, -0.070, -0.004))
    LB = 0.066
    bec = O.pointe(LB, 0.0165, 16).sculpte(lambda v: np.stack([v[:, 0] * 0.85, v[:, 1] - 0.14 * LB * (v[:, 2] / LB) ** 2.2, v[:, 2]], axis=1))
    a.piece("bec", O.couche(bec, RT @ A.cadre(Vector((0.0, -0.044, -0.008)), Vector((0.0, -1.0, -0.10)), Vector((0, 0, 1)))), BEC, poil=False)

    # ----- les ailes : noires à reflets bleus, couchées le long des flancs, la bande blanche de l'épaule sur leur bord haut -----
    for nom, c in (("G", 1), ("D", -1)):
        pts = []
        for f_, d_ in ((0.84, (c * 1.0, -0.05, 0.40)), (0.62, (c * 1.0, 0.25, 0.40)), (0.40, (c * 1.0, 0.50, 0.35)), (0.18, (c * 1.0, 0.75, 0.35))):
            p_, n_ = a.surface("corps", T @ Vector((0.0, 0.0, f_ * LC)), Vector(d_))
            pts.append(tuple(p_ + n_ * 0.005))
        pts.append((c * 0.018, 0.150, 0.150))                         # la pointe, sur la racine de la queue
        fil = K.Fil(pts, flanc=(c, 0.0, 0.0))
        LA = fil.long
        aile = A.tour(A.profil([(0, 0), (0.036, 0.06 * LA), (0.052, 0.24 * LA), (0.050, 0.50 * LA), (0.036, 0.76 * LA), (0.016, 0.93 * LA),
                                (0, LA)], 6), 36)
        aile.etire(0.30, 1.0, 1.0).sculpte(lambda v: v - np.stack([v[:, 1] ** 2 / (2.0 * 0.090), 0.0 * v[:, 1], 0.0 * v[:, 1]], axis=1))
        f = aile.v[:, 2] / LA
        ta = np.tile(NOIR, (len(f), 1))
        ta[f > 0.45] = NOIR * 0.55 + BLEU * 0.45
        # la bande blanche de l'épaule : le bord haut de l'avant de l'aile (le haut de la pièce est -Y à gauche, +Y à droite)
        ta[(f < 0.50) & (c * aile.v[:, 1] < -0.012)] = BLANC
        aile.teinte = ta
        a.piece("aile_" + nom, aile.sculpte(fil.couche), None)

    # ----- la queue : UNE longue queue étagée, serrée (trois plumes qui se chevauchent), un peu relevée ; noire puis bleue -----
    def plume(chemin, large, paliers, plat=0.24):
        p = A.courbe(chemin, 8)
        fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
        sens = np.gradient(p, fait, axis=0)
        L = float(fait[-1])
        n0 = np.array([0.0, -0.20, 0.98])

        def couche_(v):
            s = np.clip(v[:, 2], 0.0, L)
            cc = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
            tg = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
            tg /= np.linalg.norm(tg, axis=1, keepdims=True)
            x = np.cross(n0, tg)
            x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
            return cc + tg * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(tg, x)
        prof = A.profil([(0, 0), (0.70 * large, 0.05 * L), (0.95 * large, 0.30 * L), (large, 0.70 * L), (0.75 * large, 0.92 * L), (0, L)], 5)
        m = A.tour(prof, 16).etire(1.0, plat, 1.0)
        ft = m.v[:, 2] / L
        cles = [q[0] for q in paliers]
        m.teinte = np.stack([np.interp(ft, cles, [q[1][k] for q in paliers]) for k in range(3)], axis=1)
        return m.sculpte(couche_)
    S = Vector((0.0, 0.082, 0.124))                                   # dans la croupe
    dos = Vector((0.0, 0.975, 0.22)).normalized()                      # vers l'arrière, relevée de 12°
    couleurs = [(0.0, NOIR), (0.30, NOIR * 0.5 + BLEU * 0.5), (0.70, BLEU), (1.0, SARCELLE)]
    a.piece("queue", plume([tuple(S), tuple(S + dos * 0.14), tuple(S + dos * 0.29 + Vector((0, 0, 0.010)))], 0.030, couleurs), None)
    for nom, c in (("G", 1), ("D", -1)):
        d = (dos + Vector((c * 0.07, 0.0, -0.015))).normalized()
        a.piece("queue_" + nom, plume([tuple(S + Vector((c * 0.008, 0.0, -0.004))), tuple(S + d * 0.11), tuple(S + d * 0.22)], 0.026, couleurs), None)

    # ----- les pattes : noires, fines, sous le centre ; trois doigts devant, un derrière -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("patte_" + nom, O.teinte(O.tube_r([(c * 0.030, 0.006, 0.100), (c * 0.032, -0.002, 0.056), (c * 0.032, -0.008, 0.016)],
                                                  [0.0115, 0.0095, 0.0085], 12), PATTE), None, poil=False)
        doigts = None
        for ang_, long_ in ((-30, 0.034), (0, 0.040), (30, 0.034), (180, 0.024)):
            d_ = A.boule(1.0, 12, 6).etire(0.0060, 0.5 * long_, 0.0055).pose((0, -0.5 * long_, 0.0)).pose((0, 0, 0), (0, 0, ang_))
            doigts = d_ if doigts is None else doigts + d_
        a.piece("orteils_" + nom, O.teinte(doigts, PATTE), None, pos=(c * 0.032, -0.008, 0.006), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pie", styles.style_de("pie"), sys.modules[__name__]), "Pie")
