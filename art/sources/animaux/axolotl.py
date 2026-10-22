"""L'axolotl en peluche : le rose franc des grottes, une large tête plate en pelle au sourire éternel, de petits yeux noirs
posés sur les coins de la tête, et derrière elle, de chaque côté, trois branchies corail en plumeau, des tiges couvertes
de franges douces qui s'ouvrent en couronne. Un corps de salamandre couché bas sur quatre petites pattes aux doigts fins,
et une longue queue aplatie comme une rame, bordée d'une nageoire claire qui part du dos. Il ne grandira pas : il a
décidé de rester jeune pour toujours, et il en a l'air.

    python axolotl.py        fabrique la fiche art/apercus/animaux/axolotl.png (style du palier : C, velours ras)

Les 5 traits de l'axolotl (anatomie et vues de sa référence, 19/10, agent B) : 1. la tête plus LARGE que le corps, plate,
le museau carré arrondi ; 2. la bouche en sourire qui fait toute la largeur ; 3. trois paires de branchies en plumeau qui
partent de l'arrière de la tête ; 4. de petits yeux sur les côtés de la tête, sans paupière ; 5. une longue queue aplatie
sur les côtés, bordée d'une nageoire qui part du dos et fait le tour du bout.
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
import outils_a as O                          # (garde-fous : aucun tube à segment nul)

ROSE = np.array(M.hexa("#f594ae"))            # la dominante (registre : rose franc #f08ca8), un cran plus clair (style C)
DESSOUS = np.array(M.hexa("#fbc2cf"))         # le ventre
CORAIL = np.array(M.hexa("#e8567a"))          # l'accent : les branchies
OURLET = np.array(M.hexa("#f7a3b8"))          # la nageoire de la queue : un rose à peine plus clair (« #fdb0c2 » sortait blanc, une feuille)
FIL = M.hexa("#7a2c40")
TOURNE = 15                                   # la fiche tourne la tête vers la caméra (les deux yeux, le sourire) ; 0 pour le jeu
# (19/10, agent B) : la base gonflée sans renfort des parties fines (la queue en rame et la tête plate restent plates) et
# presque sans pression (une tête large gonflée redevenait une boule)
GONFLAGE_REGLAGES = {"pression": 0.10, "fins": 0.0}

HC = Vector((0.0, -0.425, 0.104))             # le centre de la tête, RELEVÉE sur les pattes avant (2e essai : à plat, l'herbe cachait le visage)


def courbure(y):
    """La queue qui s'incurve doucement sur le côté (vers +X) : rien avant y = 0,10, 7,5 cm au bout."""
    return 0.075 * np.clip((np.asarray(y, float) - 0.10) / 0.42, 0.0, None) ** 2


# du bout de la queue au bout du corps (dans la tête) : couché au sol, droit jusqu'aux hanches puis la queue qui s'incurve
_YS = np.linspace(0.53, -0.38, 14)
def hauteur(y):
    """La hauteur du fil : la queue posée, le ventre au sol, l'avant du corps qui se relève vers la tête."""
    if y > 0.10:
        return 0.062
    if y > -0.05:
        return 0.055 + 0.007 * (y + 0.05) / 0.15
    t = min(1.0, (-0.05 - y) / 0.33)
    return 0.055 + 0.045 * t * t * (3 - 2 * t)


CHEMIN = [(float(courbure(y)), float(y), hauteur(float(y))) for y in _YS]
# le rayon le long du corps (0 : le bout de la queue, 1 : le bout dans la tête)
CORPS = O.interp([(0.0, 0.0), (0.03, 0.010), (0.12, 0.020), (0.30, 0.034), (0.45, 0.046), (0.52, 0.052), (0.62, 0.060),
                  (0.78, 0.062), (0.90, 0.056), (0.96, 0.050), (1.0, 0.0)])


def construire():
    a = K.Animal("axolotl")
    a.taille = 0.52                                   # (2e essai : à 0,42 elle se noyait dans l'herbe de la fiche, comme la taupe)
    a.gonflage_reglages = dict(GONFLAGE_REGLAGES)      # lu aussi quand la fiche est lancée par essais/reel/references.py
    a.fusion_a_part = ("branchie",)                    # les franges restent des franges (fondues, elles faisaient des raquettes)

    # ----- le corps et la queue : une pièce couchée sur son fil ; le tronc un peu large, la queue APLATIE sur les côtés et
    #       haute comme une rame ; le dessous plus pâle -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(ROSE, (len(m.v), 1))
        t[ang > 2.0] = DESSOUS
        return t

    def forme(L):
        def g(v):
            s = v.copy()
            f = v[:, 2] / L
            q = K.lisse((0.60 - f) / 0.18)                 # 1 dans la queue, 0 dans le tronc
            s[:, 0] *= 1.18 - 0.68 * q                     # large au tronc, mince à la queue
            s[:, 1] *= 0.88 + 0.42 * q                     # un peu aplati au tronc, haute à la queue
            return s
        return g
    fil, L = O.fil_corps(a, "corps", CHEMIN, CORPS, peint, None, cotes=36, flanc=(1.0, 0.0, 0.0), deforme=forme)

    # ----- la nageoire : une plaque claire dans le plan du dos, basse sur le dos, plus haute sur la queue, qui fait le tour
    #       du bout et revient sous la queue jusqu'au ventre (le bas du contour est DANS le corps) -----
    # (2e essai : trop haute et trop pâle, elle faisait une grande feuille) : 0,8 à 2,1 cm au-dessus de la peau
    bord = [(-0.20, 0.105), (-0.10, 0.120), (0.00, 0.120), (0.10, 0.128), (0.20, 0.128), (0.30, 0.122), (0.38, 0.114),
            (0.46, 0.100), (0.51, 0.084), (0.530, 0.062), (0.515, 0.045), (0.46, 0.034), (0.38, 0.020), (0.28, 0.012),
            (0.18, 0.015), (0.10, 0.032), (0.06, 0.060), (-0.20, 0.080)]
    nag = O.couche(A.decoupe(bord, 0.012, 0.005), A.cadre((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0, 0, 1)))   # x -> y, y -> z
    nag.v[:, 0] += courbure(nag.v[:, 1])
    a.piece("nageoire_queue", O.teinte(nag, OURLET), None, poil=False)

    # ----- la tête : une pelle large et plate, plus large que le corps, le museau carré arrondi, le dessous pâle -----
    tete = A.boule(1.0, 56, 28)
    tete.teinte = np.where((tete.v[:, 2] < -0.45)[:, None], DESSOUS, ROSE)

    def pelle(v):
        avant = K.lisse((-v[:, 1] - 0.1) / 0.9)
        s = np.zeros_like(v)
        s[:, 0] = 0.120 * np.sign(v[:, 0]) * np.abs(v[:, 0]) ** 0.8 * (1.0 - 0.12 * avant)     # large, un peu moins au museau
        s[:, 1] = 0.095 * v[:, 1]
        s[:, 2] = 0.058 * np.sign(v[:, 2]) * np.abs(v[:, 2]) ** 0.75 * (1.0 - 0.15 * avant)    # plate, le museau plus bas
        return s
    a.piece("tete", tete.sculpte(pelle), None, pos=tuple(HC))

    # ----- le visage : deux petits yeux sur les coins de la tête (vus de face ET de trois quarts), le grand sourire -----
    O.paire_yeux(a, "tete", HC, (0.72, -0.42, 0.55), 0.0170)
    pts = []
    for ph in np.linspace(-70.0, 70.0, 15):
        r_ = math.radians(ph)
        d = Vector((math.sin(r_), -math.cos(r_), -0.20 + 0.12 * (ph / 70.0) ** 2))
        q = a.trace("tete", HC, [d], 0.002)
        if q:
            pts.append(q[0])
    if len(pts) > 1:
        a.broderie("sourire", A.courbe(pts, 3), 0.0036, FIL)

    # ----- les branchies : trois de chaque côté, de l'arrière de la tête, en couronne (la haute monte, la médiane s'ouvre,
    #       la basse part de côté), toutes rejetées vers l'arrière ; chacune une tige corail couverte de franges douces tout
    #       autour (un plumeau, pas une raquette ni un peigne) -----
    for c, nm in ((1, "G"), (-1, "D")):
        m = None
        for k, (dg, lg, zb) in enumerate((((0.35, 0.55, 0.76), 0.125, 0.098), ((0.75, 0.55, 0.37), 0.135, 0.078),
                                           ((0.88, 0.45, 0.02), 0.120, 0.054))):
            d = Vector((c * dg[0], dg[1], dg[2])).normalized()
            base = Vector((c * 0.075, -0.352, zb + (HC.z - 0.064)))     # (la tête relevée de 4 cm)
            recul = Vector((0.0, 0.030, 0.0))

            def le_long(s, d=d, base=base, lg=lg):
                return base + d * (lg * s) + recul * (s * s)
            tige = O.tube_r([tuple(le_long(s)) for s in (0.0, 0.35, 0.70, 1.0)], [0.011, 0.010, 0.008, 0.006], 10)
            bout = A.boule(1.0, 12, 6).etire(0.0072, 0.0072, 0.0072).pose(tuple(le_long(1.0)))
            morceau = O.teinte(tige, CORAIL) + O.teinte(bout, CORAIL)
            p1 = d.cross(Vector((0.0, 0.0, 1.0)))
            if p1.length < 1e-3:
                p1 = d.cross(Vector((1.0, 0.0, 0.0)))
            p1.normalize()
            p2 = d.cross(p1).normalized()
            for j, s in enumerate(np.linspace(0.20, 0.95, 14)):
                p = le_long(float(s))
                lf = 0.030 * (1.0 - 0.5 * float(s)) + 0.012
                for i3 in range(3):
                    ang = 2.0 * math.pi * i3 / 3.0 + 0.7 * j
                    dd = (p1 * math.cos(ang) + p2 * math.sin(ang)) * 0.82 + d * 0.57
                    dd.normalize()
                    frange = A.boule(1.0, 10, 6).etire(0.0042, 0.0042, lf * 0.5)
                    teinte_ = CORAIL * (1.08 if (i3 + j) % 2 else 0.96)
                    morceau = morceau + O.couche(O.teinte(frange, np.clip(teinte_, 0.0, 1.0)), A.cadre(p + dd * (lf * 0.45), dd, d))
            m = morceau if m is None else m + morceau
        a.piece("branchie_" + nm, m, None, poil=False)

    # ----- quatre petites pattes écartées, le coude en haut, la main à plat aux doigts fins écartés (4 devant, 5 derrière) -----
    for c, nm in ((1, "G"), (-1, "D")):
        for nom, r, e, w, sens, n_doigts in (("avant", (0.055, -0.25, 0.075), (0.118, -0.27, 0.070), (0.140, -0.30, 0.016), -1.0, 4),
                                             ("arriere", (0.050, 0.03, 0.045), (0.112, 0.05, 0.050), (0.140, 0.085, 0.016), 1.0, 5)):
            racine, coude, poignet = (Vector((c * p_[0], p_[1], p_[2])) for p_ in (r, e, w))
            bras = O.membre([tuple(racine), tuple(coude), tuple(poignet + Vector((0.0, 0.0, 0.004)))], [0.026, 0.021, 0.016],
                            [(1.0, tuple(ROSE))], 14)
            a.piece("patte_%s_%s" % (nom, nm), bras, None)
            paume = Vector((poignet.x, poignet.y, 0.010))
            main = O.couche(A.boule(1.0, 16, 8).etire(0.019, 0.016, 0.009), A.cadre(paume, Vector((0.0, 0.0, 1.0)), Vector((0.0, sens, 0.0))))
            for k in range(n_doigts):
                ang = math.radians(-40.0 + 80.0 * k / (n_doigts - 1))
                dd = Vector((c * math.sin(ang) * 0.9 + c * 0.25, sens * math.cos(ang), 0.0)).normalized()
                doigt = A.boule(1.0, 12, 6).etire(0.0055, 0.0055, 0.016)
                main = main + O.couche(doigt, A.cadre(paume + dd * 0.024 + Vector((0.0, 0.0, -0.002)), dd, Vector((0.0, 0.0, 1.0))))
            a.piece("pied_%s_%s" % (nom, nm), O.teinte(main, ROSE * 1.02), None, poil=False)

    a.tete = HC + Vector((0.0, -0.03, 0.01))
    if TOURNE:
        O.tourner(a, TOURNE)
    th = math.radians(TOURNE)
    a.cap_tete = Vector((math.sin(th), -math.cos(th), 0.0))    # couché au sol : la vue de près vise l'avant de la tête
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad", souple=True)


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("axolotl", styles.style_de("axolotl"), sys.modules[__name__]), "Axolotl")
