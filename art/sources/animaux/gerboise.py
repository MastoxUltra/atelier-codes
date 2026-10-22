"""La gerboise en peluche cousue main (2e dessin, 16/10, d'après les vues d'un vrai : CC-BY, rien d'importé) : une petite
boule sable rosé, le ventre crème, DRESSÉE sur ses deux seules pattes arrière comme un petit kangourou (les cuisses dans la croupe, la jambe en zigzag, de très longs pieds à plat) ; une grosse
tête sans cou, aux yeux immenses, aux grandes oreilles larges qui s'écartent en V, un museau court au petit nez rose, des
moustaches ; de minuscules mains sous le menton ; et une très longue queue fine qui descend toucher le sol derrière elle,
puis se relève, terminée par un plumet en fer de lance, noir puis blanc. Le sauteur de minuit, sur la pointe des pieds :
dans une seconde, il ne sera plus là.

    python gerboise.py        fabrique la fiche art/apercus/animaux/gerboise.png (cousu main, palier 2)

Les 5 traits de l'espèce : 1. un corps rond porté haut sur de longues pattes arrière (un mini-kangourou) ; 2. de grands
yeux noirs ; 3. de grandes oreilles larges ; 4. une queue plus longue que le corps, à plumet noir et blanc ; 5. sable dessus,
blanc dessous. (16/10 : elle était assise droite comme un lapin ; les vues du vrai la montrent la boule du corps en l'air
sur ses longues pattes, la tête dans le prolongement, la queue en balancier.)
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
import garnitures as G
import matieres as M
import peluche as K


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (deux points identiques à la suite déforment un tube en NaN)."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie


SABLE = np.array(M.hexa("#f2c8a4"))           # la dominante : sable rosé (le poil le fonce)
CLAIR = np.array(M.hexa("#fff0e0"))           # le ventre, le dedans des pattes, le plumet blanc
DOS = np.array(M.hexa("#e0aa88"))             # le dos, le dessus de la tête
ROSE = M.hexa("#f0a8a0")                      # le dedans des oreilles, le nez
NOIR = np.array(M.hexa("#2e2826"))            # les yeux, le plumet noir
LACET = 12.0                                  # la tête un peu tournée vers nous (22 : l'œil droit se voyait de profil)

# ---- les mesures, relevées sur les vues du vrai (le corps comme unité) ----
CORPS = Vector((0.0, 0.020, 0.170))           # la boule du corps, DRESSÉE (l'avant relevé de 35°) au-dessus des grands pieds
TETE = Vector((0.0, -0.070, 0.258))           # la tête posée sur l'avant du corps dressé, sans cou


def construire():
    a = K.Animal("gerboise")
    a.taille = 0.30

    # ----- le corps : une boule un peu longue, la croupe pleine, le dos plus sombre, le ventre crème -----
    def boule_(v):
        v = K.bosse(v, (0, 0.7, -0.4), 0.12, 0.45)                      # la croupe, d'où partent les cuisses
        return v * [0.068, 0.086, 0.074]
    corps = A.boule(1.0, 48, 24)
    u = corps.v
    # le ventre clair sous une ligne nette, le long des anneaux de la boule (17/10 : une limite en biais faisait une tache en étoile)
    corps.teinte = np.where((u[:, 2] > 0.25)[:, None], DOS, np.where((u[:, 2] < -0.22)[:, None], CLAIR, SABLE))
    a.piece("corps", corps.sculpte(boule_), None, pos=tuple(CORPS), rot=(-35, 0, 0))     # dressé : l'avant relevé (18/10 : à -12°,
                                                                                         # sur quatre pattes, elle faisait souris)

    # ----- la tête : grosse et ronde, le museau court, le petit nez rose ; les yeux IMMENSES ; les grandes oreilles -----
    H = A.repere(TETE, (-6, 0, LACET))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 48, 24)
    tete.sculpte(lambda v: K.bosse(v, (0, -1.0, -0.15), 0.10, 0.30))       # le museau court, à peine marqué
    tete.teinte = np.where((tete.v[:, 2] > 0.35)[:, None], DOS, SABLE)
    tete.teinte[(tete.v[:, 1] < -0.62) & (tete.v[:, 2] < 0.08) & (tete.v[:, 2] > -0.60) & (np.abs(tete.v[:, 0]) < 0.48)] = CLAIR   # le museau clair, peint
    tete.teinte[tete.v[:, 2] < -0.62] = CLAIR                                                                                       # le menton
    a.piece("tete", tete.etire(0.056, 0.058, 0.052), None, mat=H)
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.010, 0.008, 0.008), ROSE, mat=H @ A.repere((0.0, -0.066, -0.006)), poil=False)
    a.tete = H @ Vector((0.0, -0.060, -0.004))
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.56, -0.70, 0.30))                   # assez de face : les deux yeux se voient de face
        a.rustine("cerne_" + nom, "tete", H.to_translation(), regard, 0.26, tuple(NOIR), 0.003, 0)
        p, n = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0170)
        # l'oreille : grande et LARGE (une feuille), dressée et ouverte en V, un peu en arrière ; le dedans rose
        E = A.cadre(H @ Vector((c * 0.026, 0.016, 0.040)), H3 @ Vector((c * 0.50, 0.18, 0.85)), H3 @ Vector((c * 0.25, -0.95, 0.0)))
        a.piece("oreille_" + nom, A.boule(1.0, 28, 14).etire(0.032, 0.009, 0.054).pose((0, 0, 0.046)), tuple(SABLE), mat=E)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).etire(0.021, 0.008, 0.042).pose((0, 0.005, 0.048)), ROSE, mat=E, poil=False)   # devant (le +Y du repère de l'oreille : 17/10, il était au dos)
        # trois moustaches de chaque côté : de longs fils clairs BRODÉS (16/10, Art : en pièces de tissu, la base gonflée
        # les fondait dans la peau et les gonflait en un coin blanc devant le museau ; brodées, elle les refait souples)
        for k, (haut, ouvert) in enumerate(((0.010, 0.30), (0.0, 0.0), (-0.010, -0.30))):
            d = H3 @ Vector((c * 1.0, -0.40 + 0.30 * ouvert, 0.10 * ouvert * 2.0))
            dep = H @ Vector((c * 0.022, -0.056, -0.010 + haut))
            a.broderie("moustache_%s%d" % (nom, k), [tuple(dep), tuple(dep + d.normalized() * 0.045), tuple(dep + d.normalized() * 0.090)],
                       0.0014, tuple(CLAIR))

    # ----- les bras : minuscules, les mains repliées sous le menton -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.030, -0.036, 0.200), (c * 0.034, -0.056, 0.184), (c * 0.020, -0.062, 0.176)]
        a.piece("bras_" + nom, A.tube(A.courbe(propres(ch), 5), 0.0095, 10), tuple(SABLE))
        a.piece("main_" + nom, A.boule(1.0, 14, 8).etire(0.010, 0.010, 0.009), tuple(CLAIR), pos=ch[-1])

    # ----- les pattes ARRIÈRE seules la portent, comme un petit kangourou : de grosses cuisses dans la croupe, la jambe qui
    #       descend vers l'avant jusqu'au genou puis repart en arrière jusqu'au talon, et de très longs pieds à plat devant -----
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("cuisse_" + nom, A.boule(1.0, 28, 14).etire(0.040, 0.058, 0.056), tuple(SABLE), pos=(c * 0.050, 0.050, 0.130), rot=(-20, 0, c * 4))
        jam = [(c * 0.052, 0.050, 0.115), (c * 0.054, 0.004, 0.072), (c * 0.052, 0.040, 0.024)]
        a.piece("jambe_" + nom, A.tube(A.courbe(propres(jam), 6), lambda t: 0.0160 - 0.0050 * t, 12), tuple(SABLE))
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.016, 0.054, 0.011), tuple(CLAIR), pos=(c * 0.052, -0.008, 0.011), rot=(0, 0, c * 5))

    # ----- la queue : très longue et fine, elle descend toucher le sol puis se relève ; le plumet en fer de lance -----
    chemin = [(0.0, 0.080, 0.128), (0.0, 0.130, 0.072), (0.0, 0.180, 0.030), (0.004, 0.240, 0.012), (0.010, 0.300, 0.014),
              (0.014, 0.352, 0.036), (0.016, 0.392, 0.064)]

    def rayon(t):
        r = 0.0105 - 0.0045 * min(t / 0.74, 1.0)                              # fine, de plus en plus
        if t > 0.74:                                                         # le plumet : il s'élargit puis finit en pointe
            s = (t - 0.74) / 0.26
            r += 0.011 * math.sin(math.pi * min(s / 0.62, 1.0) * 0.5) * (1.0 if s < 0.62 else max(0.0, 1.0 - (s - 0.62) / 0.38) ** 0.8)
        return max(r, 0.0015)
    a.piece("queue", K.tube_peint(A.courbe(propres(chemin), 8), rayon, [(0.76, tuple(SABLE)), (0.90, tuple(NOIR)), (1.0, tuple(CLAIR))], 12), None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("gerboise", styles.style_de("gerboise"), sys.modules[__name__]), "Gerboise")
