"""Le lagopède en peluche, cinquième dessin (16/10, Art : d'après les vues d'un vrai gallinacé de la même famille, CC-BY,
regardé pour les proportions seulement, rien d'importé ; ses couleurs ne sont pas celles du lagopède). Plus d'œuf debout :
un gallinacé dodu POSÉ À L'HORIZONTALE, la poitrine ronde en avant et un peu relevée, le dos qui descend vers une
queue courte en éventail ; une petite tête ronde sur un cou court, le bec court, noir et crochu ; la caroncule vermillon
en croissant au-dessus de l'œil ; le dos, le cou et la tête grège mouchetés de brun, les ailes repliées, le ventre et
le dessous de la queue blancs, la queue noire bordée de blanc dessus ; des pattes emplumées de blanc jusqu'aux doigts.

    les 5 traits : le corps de perdrix dodu, horizontal ; la petite tête ronde au bec court et noir ; la caroncule rouge
    au-dessus de l'œil ; les pattes emplumées en chaussons blancs ; les ailes et le ventre blancs sous un manteau grège
    moucheté, la queue noire.

    python lagopede.py        fabrique la fiche art/apercus/animaux/lagopede.png (style du palier : C, velours ras)
    (refusés : trois « boules » le 15/10, puis « un œuf aux chaussons détachés et à la queue en palette » le 16/10 ;
    6e dessin le 18/10 : petite tête sur un cou court, vrai bec, ailes couchées, queue en éventail de plumes, doigts emplumés ;
    11e le 19/10 : corps plus long, tête un peu plus grosse, ailes couchées le long des flancs comme le perroquet validé,
    blanches au bout, au lieu de deux reliefs fondus qui faisaient des œufs blancs collés)
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

GREGE = np.array(M.hexa("#c4ad8e"))           # la dominante (registre : grège moucheté #cbb79a ; le velours la fonce un peu)
MOUCHE = np.array(M.hexa("#7f6a55"))          # les mouchetures
BLANC = np.array(M.hexa("#fbf9f4"))           # les ailes, le ventre, les chaussons
NOIR = np.array(M.hexa("#26211f"))            # la queue
VERMILLON = np.array(M.hexa("#ee3b22"))       # l'accent : la caroncule
CREME = np.array(M.hexa("#fffaf0"))           # le fin tour de l'œil
BEC = M.hexa("#241e1c")
TETE = Vector((0.0, -0.196, 0.336))           # (10e : devant et au-dessus du corps couché)           # (6e dessin : plus près du poitrail, sur un cou court)


def mouchetures(v, cote, rayon, graine=0, proba=0.6):
    """Vrai là où un point tombe dans une petite tache (des sphères au hasard dans un quadrillage 3D, coupées par la peau)."""
    v = np.asarray(v, float)
    base = np.floor(v / cote).astype(np.int64)
    dedans = np.zeros(len(v), bool)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                c = base + np.array([dx, dy, dz], dtype=np.int64)
                h = ((c[:, 0] * 73856093) ^ (c[:, 1] * 19349663) ^ (c[:, 2] * 83492791) ^ (graine * 40503)) & 0x7FFFFFFF

                def alea(m):
                    return ((((h * m) + 12345) >> 9) & 0xFFFF) / 65535.0
                present = alea(1103515245) < proba
                centre = (c + np.stack([alea(214013), alea(1664525), alea(22695477)], axis=1)) * cote
                r = rayon * (0.65 + 0.70 * alea(134775813))
                dedans |= present & (np.linalg.norm(v - centre, axis=1) < r)
    return dedans


def construire():
    a = K.Animal("lagopede")
    a.taille = 0.50
    a.gonflage_reglages = {"fins": 0.0, "pointes": 0.0, "pression": 0.16}   # (11e : moins gonflé, le corps restait une boule)
    a.fusion_a_part = ("queue", "aile")                   # les plumes de la queue et les ailes restent des pièces (11e : fondues,
    #                                                       les ailes faisaient deux œufs blancs collés aux flancs)

    # ----- le corps (10e passage, 18/10) : un ovale presque HORIZONTAL, 1,5 fois plus long que haut, la poitrine devant (-Y)
    #       à peine relevée ; le dessus grège moucheté, le ventre blanc -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))              # 0 : le dos ; pi : le ventre
        fr = m.v[:, 2] / L                                          # 0 : la croupe ; 1 : la poitrine
        t_ = np.tile(GREGE, (len(ang), 1))
        blanc = (ang > 1.90 + 0.50 * np.clip((fr - 0.60) / 0.35, 0.0, 1.0)) | ((fr < 0.18) & (ang > 1.30))
        t_[blanc] = BLANC                                           # le ventre et le dessous de la queue blancs
        taches = mouchetures(m.v, 0.022, 0.0068, 5, 0.75) & ~blanc
        t_[taches] = MOUCHE
        return t_
    # (6e à 9e dessins : corps dressé de 26 à 34°, tête posée dessus : une quille, « un œuf ». Ici, d'après les vues : un
    # corps de perdrix couché, la tête séparée sur un cou court, les ailes en relief, la queue relevée)
    # (11e : plus long et moins épais, 1,7 fois plus long que haut comme la gélinotte de la référence ; il reculait vers la queue)
    rayon = O.interp([(0.0, 0.0), (0.06, 0.050), (0.25, 0.088), (0.52, 0.104), (0.78, 0.099), (0.93, 0.075), (1.0, 0.034)])
    LC = 0.360
    Y0 = 0.165                                                      # la croupe
    T = O.corps_h(a, "corps", (0.0, Y0, 0.150), LC, rayon, peint, None, cotes=64, pitch=10.0,
                  deforme=O.gabarit(poitrail=0.05, ventre=0.0, croupe=0.0))

    # ----- le cou, court et MARQUÉ (plus fin que la tête : un creux à la nuque) ; la tête ronde devant et au-dessus -----
    cou = O.tube_r([(0.0, -0.118, 0.236), (0.0, -0.148, 0.282), (0.0, -0.166, 0.312)], [0.066, 0.048, 0.042], 24)
    tc = np.tile(GREGE, (len(cou.v), 1))
    tc[mouchetures(cou.v, 0.022, 0.0068, 9, 0.75)] = MOUCHE
    cou.teinte = tc
    a.piece("cou", cou, None)
    RT = A.repere(TETE, (0, 0, 16))
    tete = A.boule(1.0, 80, 40)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(GREGE, (len(u), 1))
    t[mouchetures(tete.v * 0.080, 0.020, 0.0055, 13, 0.7) & ~((u[:, 1] < -0.55) & (np.abs(u[:, 0]) < 0.50))] = MOUCHE   # pas sur la face
    OEIL_DIR = np.array([0.55, -0.78, 0.26])
    for c in (1, -1):
        e = OEIL_DIR * [c, 1, 1]
        e /= np.linalg.norm(e)
        t[(u @ e) > 0.910] = GREGE                                  # pas de moucheture autour de l'œil (pas d'œil en plus)
        t[(u @ e) > 0.9636] = CREME                                 # le fin tour clair de l'œil (l'œil couvre ~12,6°)
        cr = e * 0.80 + np.array([0.0, 0.0, 0.32])
        cr /= np.linalg.norm(cr)
        croissant = ((u @ cr) > math.cos(math.radians(14))) & ((u @ e) < math.cos(math.radians(15.5))) & (u[:, 2] > e[2] + 0.04)
        t[croissant] = VERMILLON                                    # la caroncule, en croissant au-dessus de l'œil
    tete.teinte = t
    a.piece("tete", tete.etire(0.055, 0.059, 0.052), None, mat=RT)  # (11e : un peu plus grosse, une tête de peluche)
    O.paire_yeux(a, "tete", TETE, tuple(OEIL_DIR), 0.0138, decolle=0.002, R=RT)
    a.tete = RT @ Vector((0.0, -0.063, -0.004))

    # ----- le bec : court, fort, noir, crochu, planté dans la face -----
    LB = 0.033
    bec = O.pointe(LB, 0.0175, 16).sculpte(lambda v: np.stack([v[:, 0] * 0.90, v[:, 1] - 0.30 * LB * (v[:, 2] / LB) ** 2, v[:, 2]], axis=1))
    a.piece("bec", O.couche(bec, RT @ A.cadre(Vector((0.0, -0.047, -0.008)), Vector((0.0, -1.0, -0.10)), Vector((0, 0, 1)))), BEC, poil=False)

    # ----- les ailes repliées, COUCHÉES le long des flancs (11e, la méthode du perroquet validé) : chacune suit des points
    #       relevés sur le corps, de l'épaule à la racine de la queue, à plat et bombée comme le flanc ; les couvertures grège
    #       mouchetées à l'épaule, puis les grandes plumes blanches du lagopède jusqu'à la pointe, sur la queue -----
    for nom, c in (("G", 1), ("D", -1)):
        pts = []
        for f_, d_ in ((0.80, (c * 1.0, -0.10, 0.30)), (0.60, (c * 1.0, 0.15, 0.22)), (0.40, (c * 1.0, 0.35, 0.18)), (0.20, (c * 1.0, 0.60, 0.22))):
            p_, n_ = a.surface("corps", T @ Vector((0.0, 0.0, f_ * LC)), Vector(d_))
            pts.append(tuple(p_ + n_ * 0.008))
        pts.append((c * 0.024, Y0 + 0.012, 0.192))                    # la pointe, posée sur la racine de la queue
        fil = K.Fil(pts, flanc=(c, 0.0, 0.0))
        LA = fil.long
        aile = A.tour(A.profil([(0, 0), (0.040, 0.08 * LA), (0.058, 0.28 * LA), (0.056, 0.52 * LA), (0.042, 0.74 * LA), (0.022, 0.91 * LA),
                                (0, LA)], 6), 36)
        aile.etire(0.36, 1.0, 1.0).sculpte(lambda v: v - np.stack([v[:, 1] ** 2 / (2.0 * 0.110), 0.0 * v[:, 1], 0.0 * v[:, 1]], axis=1))  # bombée
        f = aile.v[:, 2] / LA
        ta = np.tile(BLANC, (len(f), 1))
        cv = f < 0.36                                                 # les couvertures, à l'épaule
        ta[cv] = GREGE
        ta[cv & mouchetures(aile.v * 0.9, 0.020, 0.0062, 21 + c, 0.7)] = MOUCHE
        aile.teinte = ta
        a.piece("aile_" + nom, aile.sculpte(fil.couche), None)

    # ----- la queue : un éventail de plumes qui sort de la croupe et tombe un peu ; noire, le bout blanc ; les couvertures
    #       blanches dessus -----
    def plume(chemin, large, paliers, plat=0.26):
        p = A.courbe(chemin, 8)
        fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
        sens = np.gradient(p, fait, axis=0)
        L = float(fait[-1])
        n0 = np.array([0.0, -0.22, 0.975])                               # la face de l'éventail : vers le ciel

        def couche_(v):
            s = np.clip(v[:, 2], 0.0, L)
            cc = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
            tg = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
            tg /= np.linalg.norm(tg, axis=1, keepdims=True)
            x = np.cross(n0, tg)
            x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
            return cc + tg * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(tg, x)
        prof = A.profil([(0, 0), (0.60 * large, 0.06 * L), (0.90 * large, 0.30 * L), (large, 0.62 * L), (0.86 * large, 0.86 * L),
                         (0.45 * large, 0.97 * L), (0, L)], 5)
        m = A.tour(prof, 16).etire(1.0, plat, 1.0)
        ft = m.v[:, 2] / L
        tq = np.tile(np.asarray(paliers[0][1], float), (len(ft), 1))
        for seuil, col in paliers[1:]:
            tq[ft > seuil] = col
        m.teinte = tq
        return m.sculpte(couche_)
    S = Vector((0.0, Y0 - 0.010, 0.166))              # la croupe
    dos = Vector((0.0, 0.990, 0.10)).normalized()     # à peine relevée (11e : de dos, elle faisait une palette plate dressée)
    for k, ang in enumerate((-24, -12, 0, 12, 24)):
        d = (dos * math.cos(math.radians(ang)) + Vector((1.0, 0.0, 0.0)) * math.sin(math.radians(ang))).normalized()
        long_ = 0.112 - 0.010 * abs(ang) / 24.0
        ch = [tuple(S + Vector((0.004 * ang / 24.0, 0, 0))), tuple(S + d * (0.5 * long_) + Vector((0, 0, 0.001))), tuple(S + d * long_ + Vector((0, 0, -0.004)))]
        a.piece("queue_%d" % k, plume(ch, 0.022, [(0.0, NOIR), (0.86, BLANC)], plat=0.34), None)
    a.piece("queue_dessus", plume([tuple(S + Vector((0, -0.010, 0.012))), tuple(S + dos * 0.035 + Vector((0, 0, 0.012))),
                                   tuple(S + dos * 0.072 + Vector((0, 0, 0.006)))], 0.030, [(0.0, BLANC)]), None)

    # ----- les pattes : courtes, emplumées de blanc jusqu'aux doigts ; trois doigts devant, un derrière, emplumés -----
    for nom, c in (("G", 1), ("D", -1)):
        jambe = O.tube_r([(c * 0.044, -0.020, 0.105), (c * 0.048, -0.030, 0.062), (c * 0.050, -0.040, 0.026)], [0.033, 0.029, 0.025], 18)
        a.piece("patte_" + nom, O.teinte(jambe, BLANC), None)
        doigts = None
        for ang_, long_ in ((-30, 0.044), (0, 0.050), (30, 0.044), (180, 0.026)):
            d_ = A.boule(1.0, 16, 8).etire(0.0105, 0.5 * long_, 0.0095).pose((0, -0.5 * long_, 0.0)).pose((0, 0, 0), (0, 0, ang_))
            doigts = d_ if doigts is None else doigts + d_
        a.piece("orteils_" + nom, O.teinte(doigts, BLANC), None, pos=(c * 0.050, -0.040, 0.011))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lagopede", styles.style_de("lagopede"), sys.modules[__name__]), "Lagopède")
