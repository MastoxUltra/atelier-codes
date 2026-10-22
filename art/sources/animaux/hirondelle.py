"""L'hirondelle en peluche (3e dessin, 18/10, Art : d'après les vues d'une vraie, CC-BY, rien d'importé) : une petite flèche
bleu nuit luisant posée presque à l'horizontale, le ventre crème ; le front et la gorge brique, peints sur la tête, et
sous la gorge un collier bleu nuit ; un tout petit bec noir, court et large, comme un triangle ; de longues ailes pointues
qui croisent derrière, au-delà de la croupe ; et la queue en ciseaux : deux longs filets qui s'écartent en V. Elle vient
de se poser, elle repart dans une seconde.

    python hirondelle.py        fabrique la fiche art/apercus/animaux/hirondelle.png (style du palier : A, cousu main)

Les 5 traits de l'espèce : 1. la queue fourchue aux longs filets ; 2. les ailes longues et pointues ; 3. le dos bleu nuit
luisant, le ventre crème ; 4. le front et la gorge brique, le collier bleu ; 5. un bec minuscule, large à la base.
(16/10, planche 16 : « refais le bec de l'hirondelle » : il était long et fin, un bec de passereau ; le vrai est un petit
triangle. Les taches brique étaient deux boules posées sur la face : elles sont peintes.)
(4e, 19/10 : de face, une boule bleue où la tête se fondait au corps, et l'œil droit sur le bord : corps plus fin et moins
gonflé, cou marqué, tête moins tournée, yeux un peu plus vers l'avant ; le front brique en petite calotte ronde.)
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

NUIT = np.array(M.hexa("#2a3f8e"))            # la dominante (registre : bleu nuit luisant) ; le poil fonce un peu
NUIT_F = np.array(M.hexa("#1f2e6a"))          # le bout des ailes, la queue
CREME = np.array(M.hexa("#f7ecd2"))           # le ventre
BRIQUE = np.array(M.hexa("#c4502f"))          # l'accent : la gorge, le front
BEC = M.hexa("#2a2528")
PATTE = M.hexa("#5a4640")

CROUPE = (0.0, 0.080, 0.050)                  # le centre de la croupe (le corps couché part de là vers l'avant)
LC = 0.180                                    # la longueur du corps
PENTE = 22.0                                  # la poitrine relevée de 30°
TETE = Vector((0.0, -0.092, 0.132))
LACET = 10.0                                   # (4e : 18°, l'œil droit passait sur le bord de face)


def construire():
    a = K.Animal("hirondelle")
    a.taille = 0.32                           # les filets de la queue compris
    a.fusion_a_part = ("aile", "queue")       # les ailes et les plumes de la queue restent des pièces
    a.gonflage_reglages = {"pression": 0.14}  # (4e : moins gonflée, elle faisait une boule de poussin)

    # ----- le corps : un fuseau effilé, couché, la poitrine relevée ; le dos bleu nuit, le ventre crème, le collier bleu -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))              # 0 : le dos ; pi : le ventre
        fr = m.v[:, 2] / L                                          # 0 : la croupe ; 1 : la poitrine
        t_ = np.tile(NUIT, (len(ang), 1))
        t_[(ang > 1.55) & (fr < 0.80)] = CREME                      # le ventre
        t_[(ang > 1.85) & (fr < 0.25)] = CREME                      # le dessous de la queue
        return t_
    rayon = O.interp([(0.0, 0.0), (0.08, 0.022), (0.30, 0.038), (0.58, 0.044), (0.82, 0.041), (0.95, 0.028), (1.0, 0.012)])   # (4e : plus fin, un fuseau)
    T = O.corps_h(a, "corps", CROUPE, LC, rayon, peint, None, cotes=48, pitch=PENTE)

    # ----- la tête : ronde, un peu aplatie, dans le prolongement du corps ; le front et la gorge brique PEINTS -----
    RT = A.repere(TETE, (0, 0, LACET))
    tete = A.boule(1.0, 48, 24)
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    tt = np.tile(NUIT, (len(u), 1))
    # (2e : plus petites ; tout le visage brique faisait un masque) : le front juste au-dessus du bec, la gorge sous le bec
    front = np.array([0.0, -0.90, 0.44]) / np.linalg.norm([0.0, -0.90, 0.44])
    tt[(u @ front) > math.cos(math.radians(21))] = BRIQUE           # (4e : une petite calotte ronde au-dessus du bec, plus une barre)
    tt[(u[:, 2] < -0.28) & (u[:, 1] < -0.22) & (np.abs(u[:, 0]) < 0.58)] = BRIQUE
    tete.teinte = tt
    a.piece("tete", tete.etire(0.033, 0.038, 0.031), None, mat=RT)
    a.piece("cou", O.teinte(O.tube_r([(0.0, -0.050, 0.100), (0.0, -0.070, 0.114), (0.0, -0.084, 0.126)], [0.036, 0.030, 0.027], 20), NUIT), None)
    O.paire_yeux(a, "tete", TETE, (0.54, -0.77, 0.28), 0.0094, decolle=0.002, R=RT)   # (4e : un peu plus vers l'avant, les deux se voient de face)
    a.tete = RT @ Vector((0.0, -0.044, 0.0))

    # ----- le bec : minuscule, noir, large à la base et court, un petit triangle un peu aplati -----
    LB = 0.026
    bec = O.pointe(LB, 0.0105, 16).etire(1.25, 0.70, 1.0)
    a.piece("bec", O.couche(bec, RT @ A.cadre(Vector((0.0, -0.027, -0.004)), Vector((0.0, -1.0, -0.12)), Vector((0, 0, 1)))), BEC, poil=False)

    # ----- les ailes : longues et pointues, couchées le long des flancs, elles croisent au-delà de la croupe -----
    for nom, c in (("G", 1), ("D", -1)):
        pts = []
        for f_, d_ in ((0.84, (c * 1.0, -0.10, 0.25)), (0.62, (c * 1.0, 0.20, 0.25)), (0.40, (c * 1.0, 0.45, 0.20)), (0.18, (c * 1.0, 0.70, 0.25))):
            p_, n_ = a.surface("corps", T @ Vector((0.0, 0.0, f_ * LC)), Vector(d_))
            pts.append(tuple(p_ + n_ * 0.004))
        pts.append((c * 0.010, 0.140, 0.069))                         # la pointe, au-dessus de la queue
        pts.append((-c * 0.008, 0.180, 0.066))                        # ... croisée
        fil = K.Fil(pts, flanc=(c, 0.0, 0.0))
        LA = fil.long
        aile = A.tour(A.profil([(0, 0), (0.020, 0.06 * LA), (0.030, 0.22 * LA), (0.026, 0.48 * LA), (0.016, 0.74 * LA), (0.007, 0.92 * LA),
                                (0, LA)], 6), 32)
        aile.etire(0.30, 1.0, 1.0).sculpte(lambda v: v - np.stack([v[:, 1] ** 2 / (2.0 * 0.050), 0.0 * v[:, 1], 0.0 * v[:, 1]], axis=1))
        f = aile.v[:, 2] / LA
        ta = np.tile(NUIT, (len(f), 1))
        ta[f > 0.55] = NUIT_F
        aile.teinte = ta
        a.piece("aile_" + nom, aile.sculpte(fil.couche), None)

    # ----- la queue en ciseaux : deux longs filets qui s'écartent en V, et deux plumes courtes entre eux -----
    def plume(chemin, large, couleur, plat=0.30):
        p = A.courbe(chemin, 8)
        fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
        sens = np.gradient(p, fait, axis=0)
        L = float(fait[-1])
        n0 = np.array([0.0, 0.0, 1.0])

        def couche_(v):
            s = np.clip(v[:, 2], 0.0, L)
            cc = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
            tg = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
            tg /= np.linalg.norm(tg, axis=1, keepdims=True)
            x = np.cross(n0, tg)
            x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
            return cc + tg * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(tg, x)
        prof = A.profil([(0, 0), (0.80 * large, 0.05 * L), (large, 0.25 * L), (0.70 * large, 0.60 * L), (0.40 * large, 0.88 * L), (0, L)], 5)
        m = A.tour(prof, 14).etire(1.0, plat, 1.0)
        m.teinte = np.tile(np.asarray(couleur, float), (len(m.v), 1))
        return m.sculpte(couche_)
    S = Vector((0.0, 0.072, 0.060))                   # dans la croupe
    for nom, c in (("G", 1), ("D", -1)):
        d = Vector((c * math.sin(math.radians(16)), math.cos(math.radians(16)), -0.04)).normalized()   # (2e : plus longs, plus larges, plus écartés)
        a.piece("queue_filet_" + nom, plume([tuple(S), tuple(S + d * 0.120), tuple(S + d * 0.250 + Vector((0, 0, -0.002)))], 0.0130, NUIT_F), None)
        d2 = Vector((c * math.sin(math.radians(6)), math.cos(math.radians(6)), -0.12)).normalized()
        a.piece("queue_" + nom, plume([tuple(S + Vector((0, 0, 0.004))), tuple(S + d2 * 0.040), tuple(S + d2 * 0.078)], 0.014, NUIT_F), None)

    # ----- les pattes : minuscules, sombres, sous le ventre ; trois doigts devant, un derrière -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("patte_" + nom, O.teinte(O.tube_r([(c * 0.018, 0.004, 0.052), (c * 0.020, -0.002, 0.028), (c * 0.020, -0.006, 0.010)],
                                                  [0.0065, 0.0055, 0.0050], 10), np.asarray(PATTE, float)), None, poil=False)
        doigts = None
        for ang_, long_ in ((-28, 0.018), (0, 0.021), (28, 0.018), (180, 0.012)):
            d_ = A.boule(1.0, 12, 6).etire(0.0035, 0.5 * long_, 0.0032).pose((0, -0.5 * long_, 0.0)).pose((0, 0, 0), (0, 0, ang_))
            doigts = d_ if doigts is None else doigts + d_
        a.piece("orteils_" + nom, doigts, PATTE, pos=(c * 0.020, -0.006, 0.0035), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("hirondelle", styles.style_de("hirondelle"), sys.modules[__name__]), "Hirondelle")
