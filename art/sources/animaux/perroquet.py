"""Le perroquet en peluche : un ara écarlate (3e dessin, 16-17/10, d'après l'anatomie de l'ara : la référence CC-BY reçue était un personnage de dessin animé, écartée).
Debout sur le sol, le corps penché en avant, la tête ronde portée haut, d'un rouge franc ; la face nue blanche autour de
l'œil ; le gros bec crochu ivoire, la pointe sombre, la mandibule du bas noire ; les ailes repliées sur les flancs, rouges à
l'épaule, une large bande jaune, puis le bleu roi des grandes plumes ; et la queue, longue et pointue, rouge au bout bleu, qui
file derrière lui jusqu'au sol. Il penche la tête : il vous a déjà entendu parler, et il va le répéter.

    python perroquet.py        fabrique la fiche art/apercus/animaux/perroquet.png (style du palier)

Les 5 traits de l'espèce (ara macao) : 1. tout rouge écarlate ; 2. la face nue blanche autour de l'œil ; 3. un énorme bec
crochu, clair dessus, noir dessous ; 4. les ailes : bande jaune puis bleu roi ; 5. une queue très longue et pointue.
(15/10, planche 13 : « hideux » : la tête était une boule posée sur le corps, la face une plaque blanche, le bec tombait comme
une langue, les yeux fâchés sous des rides. Refait d'après les proportions d'un vrai ara : la tête tient au corps par le cou,
la face est peinte, le bec est un vrai crochet dur, les yeux ronds et ouverts.)
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

ECARLATE = np.array(M.hexa("#f2392a"))        # la dominante (registre : écarlate franc)
ROUGE_DOS = np.array(M.hexa("#e0322a"))       # le dos, un cran plus sombre
ROI = np.array(M.hexa("#2f62e0"))             # l'accent : le bleu roi des grandes plumes et du bout de la queue
CIEL = np.array(M.hexa("#4f8ae8"))            # le bleu plus clair du croupion
JAUNE = np.array(M.hexa("#ffd22a"))           # la bande jaune des ailes
FACE = np.array(M.hexa("#fbf6ee"))            # la face nue
IVOIRE = np.array(M.hexa("#f3e6cf"))          # le dessus du bec
POINTE = np.array(M.hexa("#3a3436"))          # la pointe du bec
NOIR_BEC = M.hexa("#d6c9b4")                  # (4e passage : la mandibule du bas, corne foncée ; grise ou noire, elle se lisait comme une bouche ouverte)                  # la mandibule du bas
PATTE = M.hexa("#6c6670")                     # les pattes, gris sombre

# ---- les mesures (d'après l'anatomie de l'ara macao) ----
BASE = Vector((0.0, 0.060, 0.120))            # le bas du corps (le croupion)
PENTE = 28.0                                  # le corps penché vers l'avant (degrés depuis la verticale ; le vrai, perché : ~40°)
LONG = 0.290                                  # la longueur du corps
TETE = Vector((0.0, -0.108, 0.452))
TETE_R = (0.071, 0.077, 0.073)                # (2e passage : un peu plus grosse, une tête de peluche)
LACET = 16.0                                  # la tête un peu tournée vers nous


def construire():
    a = K.Animal("perroquet")
    a.taille = 0.85
    a.fusion_a_part = ("aile", "queue")       # les ailes et la queue restent des pièces : on les lit (pas de boudin gonflé)

    # ----- le corps : un œuf penché vers l'avant, le poitrail bombé, le dos un peu plus sombre -----
    T = A.repere(BASE, (PENTE, 0, 0))
    pc = A.profil([(0, 0.0), (0.050, 0.012), (0.078, 0.050), (0.090, 0.110), (0.088, 0.170), (0.076, 0.225), (0.058, 0.265),
                   (0, LONG)], 6)
    corps = A.tour(pc, 52)

    def galbe(v):
        s = v.copy()
        f = np.clip(v[:, 2] / LONG, 0, 1)
        s[:, 1] = np.where(v[:, 1] < 0, v[:, 1] * (1.0 + 0.12 * np.sin(np.pi * f)), v[:, 1] * 0.88)    # le poitrail devant
        return s
    corps.sculpte(galbe)
    ang = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))          # 0 : le dos (+Y de la pièce, derrière)
    t = np.tile(ECARLATE, (len(ang), 1))
    t[ang < 0.9] = ROUGE_DOS
    corps.teinte = t
    a.piece("corps", corps, None, mat=T)
    haut = Vector(T @ Vector((0, 0, 0.250)))

    # ----- le cou, court et plein : la tête TIENT au corps -----
    RT = A.repere(TETE, (-4, 0, LACET))
    cou = O.tube_r([tuple(haut + Vector((0, 0.020, -0.040))), tuple(haut + Vector((0, -0.006, 0.030))),
                    tuple(RT @ Vector((0, 0.010, -0.020)))], [0.074, 0.066, 0.058], 22)
    a.piece("cou", O.teinte(cou, ECARLATE), None)

    # ----- la tête : ronde, rouge ; la face nue blanche peinte autour de l'œil (plus de plaque cousue) -----
    tete = A.boule(1.0, 56, 28)
    tete.sculpte(lambda v: K.bosse(v, (0, -0.3, 0.9), 0.06, 0.35))   # le front un peu haut
    u = tete.v / np.maximum(np.linalg.norm(tete.v, axis=1, keepdims=True), 1e-9)
    tt = np.tile(ECARLATE, (len(u), 1))
    nue = (u[:, 1] < 0.08) & (np.abs(u[:, 0]) > 0.30) & (u[:, 2] > -0.52) & (u[:, 2] < 0.50)
    tt[nue] = FACE
    tete.teinte = tt
    a.piece("tete", tete.etire(*TETE_R), None, mat=RT)
    a.tete = RT @ Vector((0.0, -0.100, -0.020))
    O.paire_yeux(a, "tete", TETE, (0.62, -0.70, 0.22), 0.0165, decolle=0.003, R=RT)

    # ----- le bec : un gros crochet dur, ivoire dessus, la pointe sombre, qui se recourbe vers le bas ; la mandibule noire -----
    # (2e passage, 17/10 : le 1er bec, un cône penché, faisait un bec de corbeau ; celui de l'ara est un CROCHET : haut à la
    # base, il avance puis plonge, la pointe tournée vers le bas et un peu en arrière, au niveau du menton. Il suit donc un
    # chemin courbe dans la tête, une pièce tournée couchée le long de ce chemin ; la mandibule du bas, noire, sous le crochet)
    R3 = RT.to_3x3()
    flanc = R3 @ Vector((1.0, 0.0, 0.0))

    def corne(chemin, rayons, large, paliers, nom):
        fil = K.Fil([tuple(RT @ Vector(q)) for q in chemin], flanc=tuple(flanc))
        L = fil.long
        m = A.tour(A.profil([(r * 1.0, f * L) for f, r in rayons], 6), 36).etire(large, 1.0, 1.0)
        f = np.clip(m.v[:, 2] / L, 0, 1)
        tb = np.tile(np.asarray(paliers[0][1], float), (len(f), 1))
        for seuil, col in paliers[1:]:
            tb[f > seuil] = col
        m.teinte = tb
        a.piece(nom, m.sculpte(fil.couche), None, poil=False)
    corne([(0.0, -0.046, 0.006), (0.0, -0.080, 0.006), (0.0, -0.104, -0.008), (0.0, -0.117, -0.032), (0.0, -0.113, -0.058),
           (0.0, -0.103, -0.074)],
          [(0.0, 0.0), (0.04, 0.030), (0.16, 0.035), (0.32, 0.033), (0.50, 0.027), (0.68, 0.019), (0.84, 0.011), (0.95, 0.005), (1.0, 0.0)],
          0.88, [(0.0, IVOIRE), (0.80, POINTE)], "bec")
    # (3e passage : plus grosse, plus basse, gris sombre : noire et en retrait, elle se lisait comme une bouche ouverte)
    corne([(0.0, -0.046, -0.030), (0.0, -0.074, -0.042), (0.0, -0.096, -0.054)],
          [(0.0, 0.0), (0.08, 0.022), (0.30, 0.027), (0.62, 0.024), (0.86, 0.016), (1.0, 0.0)],
          0.90, [(0.0, np.asarray(NOIR_BEC, float))], "bec_bas")

    # ----- les ailes repliées sur les flancs : rouges à l'épaule, la large bande jaune, puis le bleu roi des grandes plumes -----
    #       (chacune couchée le long du flanc, sur des points relevés sur le corps : ni enfouie au milieu ni décollée au bout ;
    #       les pointes croisent au-dessus de la racine de la queue)
    for nom, c in (("G", 1), ("D", -1)):
        pts = []
        for f_, d_ in ((0.84, (c * 1.0, -0.15, 0.10)), (0.64, (c * 1.0, 0.20, 0.0)), (0.44, (c * 1.0, 0.45, -0.05)), (0.24, (c * 1.0, 0.75, -0.10))):
            p_, n_ = a.surface("corps", T @ Vector((0.0, 0.0, f_ * LONG)), Vector(d_))
            pts.append(tuple(p_ + n_ * 0.012))
        pts.append((c * 0.034, 0.190, 0.130))
        pts.append((c * 0.022, 0.262, 0.108))                         # les longues ailes du vrai : la pointe sur la queue
        fil = K.Fil(pts, flanc=(c, 0.0, 0.0))
        LA = fil.long
        aile = A.tour(A.profil([(0, 0), (0.046, 0.08 * LA), (0.070, 0.26 * LA), (0.070, 0.50 * LA), (0.054, 0.72 * LA), (0.030, 0.90 * LA),
                                (0, LA)], 6), 36)
        f = aile.v[:, 2] / LA
        ta = np.tile(ECARLATE, (len(f), 1))
        ta[f > 0.24] = JAUNE
        ta[f > 0.44] = ROI
        aile.teinte = ta
        a.piece("aile_" + nom, aile.etire(0.40, 1.0, 1.0).sculpte(fil.couche), None)

    # ----- la queue : longue et pointue, rouge, le bout bleu roi ; deux plumes bleues plus courtes de chaque côté -----
    def plume(chemin, large, long_paliers, plat=0.28):
        p = A.courbe(chemin, 8)
        fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
        sens = np.gradient(p, fait, axis=0)
        L = float(fait[-1])
        n0 = np.array([0.0, 0.0, 1.0])                                  # à plat : la face vers le ciel

        def couche_(v):
            s = np.clip(v[:, 2], 0.0, L)
            cc = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
            tg = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
            tg /= np.linalg.norm(tg, axis=1, keepdims=True)
            x = np.cross(n0, tg)
            x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
            return cc + tg * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(tg, x)
        prof = A.profil([(0, 0), (0.70 * large, 0.04 * L), (large, 0.20 * L), (0.92 * large, 0.50 * L), (0.62 * large, 0.80 * L),
                         (0.26 * large, 0.96 * L), (0, L)], 5)
        m = A.tour(prof, 16).etire(1.0, plat, 1.0)
        ft = m.v[:, 2] / L
        tq = np.zeros((len(ft), 3))
        reste = np.ones(len(ft), bool)
        for fr, col in long_paliers:
            ici = reste & (ft <= fr)
            tq[ici] = col
            reste &= ~ici
        tq[reste] = long_paliers[-1][1]
        m.teinte = tq
        return m.sculpte(couche_)
    # (2e passage, 17/10 : plus longue, et en peluche comme le corps : lisse, son rouge se lisait rose)
    milieu = [(0.0, 0.080, 0.150), (0.0, 0.190, 0.104), (0.0, 0.330, 0.058), (0.0, 0.480, 0.030), (0.0, 0.620, 0.018), (0.0, 0.740, 0.014)]
    a.piece("queue", plume(milieu, 0.044, [(0.66, ECARLATE), (1.0, ROI)]), None)
    for nom, c in (("G", 1), ("D", -1)):
        cote = [(c * 0.016, 0.080, 0.146), (c * 0.032, 0.190, 0.098), (c * 0.050, 0.320, 0.052), (c * 0.064, 0.430, 0.026), (c * 0.074, 0.520, 0.018)]
        a.piece("queue_" + nom, plume(cote, 0.032, [(0.36, ECARLATE), (1.0, ROI)], 0.26), None)

    # ----- les pattes : des culottes rouges, de courtes pattes grises, deux doigts devant et deux derrière -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("culotte_" + nom, A.boule(1.0, 28, 14).etire(0.040, 0.050, 0.054), tuple(ECARLATE), pos=(c * 0.046, 0.010, 0.120))
        ch = [(c * 0.044, 0.004, 0.096), (c * 0.046, -0.004, 0.056), (c * 0.046, -0.010, 0.022)]
        a.piece("patte_" + nom, A.tube(A.courbe(ch, 5), 0.0135, 12), PATTE, poil=False)
        doigts = None
        for ang, long_ in ((-22, 0.040), (22, 0.040), (160, 0.030), (200, 0.030)):
            d = A.boule(1.0, 14, 7).etire(0.0085, long_ * 0.5, 0.0085).pose((0, -long_ * 0.5, 0.0)).pose((0, 0, 0), (0, 0, ang))
            doigts = d if doigts is None else doigts + d
        a.piece("orteils_" + nom, doigts, PATTE, pos=(c * 0.046, -0.010, 0.009), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("perroquet", styles.style_de("perroquet"), sys.modules[__name__]), "Perroquet")
