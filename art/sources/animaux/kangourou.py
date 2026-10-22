"""Le kangourou en peluche de velours ras (3e dessin, 19/10, d'après les vues du vrai : le modèle de référence CC-BY de
references_3d/kangourou, rien d'importé). Un roux miel chaud, le ventre et le bas du museau crème. Il se tient comme le
vrai au repos : DRESSÉ en trépied sur ses deux très longs pieds à plat et sa grosse queue couchée au sol derrière lui, le
torse penché un peu en avant, les cuisses puissantes en jambons, de petits bras repliés devant la poitrine, les mains
tombantes ; une tête de biche au long museau doux, au nez sombre, aux grands yeux et aux grandes oreilles pointues
dressées en V. Le guetteur du bush : il a entendu quelque chose et vous regarde, prêt à bondir.

    python kangourou.py        fabrique la fiche art/apercus/animaux/kangourou.png (velours ras, palier 3)

Les 5 traits de l'espèce : 1. dressé sur des pieds immenses (plus longs que la tête), les cuisses énormes dans la croupe ;
2. une queue longue et épaisse, large à la base, couchée au sol comme une troisième patte ; 3. de petits bras courts
repliés devant ; 4. une tête de biche au museau allongé et de grandes oreilles pointues dressées ; 5. roux dessus, crème
dessous. (18/10 refusé : fait à la main, assis en poire, la tête vue de face en boule crème.)

Les mesures relevées sur la référence (hauteur au bout des oreilles = 1) : pied 0,33 de long, au sol ; cuisses de 0,18 à
0,45 de haut, 0,43 de large à elles deux ; queue de 0,60 de long au sol derrière ; torse penché de 25° ; tête 0,30 de long,
museau à 0,80 ; oreilles 0,13. La peluche garde ces rapports, la tête un peu plus grosse et le torse un peu plus droit.
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


def propres(points, eps=2e-4):
    """Les points d'un tracé sans doublons consécutifs (un tube dont deux points se suivent à l'identique se déforme en NaN) ;
    au moins deux points, écartés d'un millimètre au pire."""
    sortie = []
    for q in points:
        if not sortie or (np.asarray(q, float) - np.asarray(sortie[-1], float)).dot(np.asarray(q, float) - np.asarray(sortie[-1], float)) > eps * eps:
            sortie.append(q)
    if len(sortie) < 2:
        base = sortie[0] if sortie else Vector((0.0, 0.0, 0.0))
        sortie = [base, Vector(base) + Vector((0.0, 0.0, 0.001))]
    return sortie


ROUX = np.array(M.hexa("#f2a560"))            # la dominante : roux miel (le poil la fonce : on la prend claire)
CLAIR = np.array(M.hexa("#ffe2b4"))           # le ventre, le bas du museau, le dedans des oreilles
BRUN = np.array(M.hexa("#6a4630"))            # l'accent : le bout des pieds, les mains, le bout des oreilles et de la queue
NEZ = M.hexa("#3a2a28")

# ---- les mesures (la peluche : 1,42 au bout des oreilles ; la référence × 1,3, la tête un peu plus grosse) ----
CORPS = Vector((0.0, -0.100, 0.620))          # le torse, penché en avant de 20°
TETE = Vector((0.0, -0.400, 1.080))           # la tête, au bout d'un cou court qui part en avant
PENTE = 12.0                                  # le museau un peu vers le bas, comme le vrai
LACET = 10.0                                  # la tête à peine tournée vers nous : le long museau se voit de trois quarts


def construire():
    a = K.Animal("kangourou")
    a.taille = 1.80

    # ----- le torse : une poire penchée en avant, profonde et étroite, le ventre crème devant -----
    corps = A.boule(1.0, 56, 28)
    v = corps.v
    corps.teinte = np.where(((v[:, 1] < -0.30) & (v[:, 2] < 0.78) & (v[:, 2] > -0.85))[:, None], CLAIR, ROUX)

    def poire(v):
        v = K.bosse(v, (0, -0.9, 0.2), 0.08, 0.40)                       # la poitrine un peu bombée
        s = v * [0.175, 0.200, 0.340]
        s[:, 0] *= 1 + 0.22 * K.lisse((-v[:, 2] + 0.2) / 1.0)            # plus large en bas, vers les hanches
        return s
    a.piece("corps", corps.sculpte(poire), None, pos=CORPS, rot=(20, 0, 0))

    # ----- le cou : court et épais, il part en avant du haut du torse -----
    a.piece("cou", A.tube(A.courbe(propres([(0.0, -0.170, 0.840), (0.0, -0.235, 0.935), (0.0, -0.300, 1.015)]), 6),
                          lambda t: 0.112 - 0.016 * t, 18), tuple(ROUX))

    # ----- la tête de biche : le crâne rond, le long museau qui s'amincit, le nez sombre au bout -----
    H = A.repere(TETE, (PENTE, 0, LACET))
    H3 = H.to_3x3()
    tete = A.tour(A.profil([(0, 0), (0.075, 0.012), (0.120, 0.050), (0.138, 0.110), (0.134, 0.170), (0.115, 0.235),
                            (0.092, 0.300), (0.076, 0.360), (0.064, 0.410), (0.048, 0.455), (0, 0.480)], 6), 48)
    tete.etire(1.0, 0.92, 1.0)
    u = tete.v                                                            # repère du tour : x = travers, y = haut, z = long
    t = np.tile(ROUX, (len(u), 1))
    t[(u[:, 2] > 0.300) & (u[:, 1] < 0.012)] = CLAIR                     # le bas du museau et les lèvres
    t[(u[:, 2] > 0.170) & (u[:, 1] < -0.070)] = CLAIR                    # le menton, jusque sous la joue
    tete.teinte = t
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0.170, -0.020), (90, 0, 0)))
    a.piece("truffe", A.boule(1.0, 24, 12).etire(0.036, 0.024, 0.026), NEZ, mat=H @ A.repere((0, -0.296, 0.004)), poil=False)
    a.tete = H @ Vector((0, -0.160, 0.0))
    fw_ = H3 @ Vector((0, -1, 0))
    a.cap_tete = Vector((fw_.x, fw_.y, 0.0)).normalized()               # le gros plan se place devant la tête : les deux yeux se voient
    bouche = [H3 @ Vector(d) for d in ((-0.40, -0.70, -0.60), (0.0, -0.80, -0.62), (0.40, -0.70, -0.60))]
    a.broderie("bouche", A.courbe(propres(a.trace("tete", H @ Vector((0, -0.215, -0.010)), bouche, 0.004)), 4), 0.0026, NEZ)

    # ----- les yeux : grands, ronds et ouverts, assez de face ; les oreilles : grandes, pointues, dressées en V -----
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.52, -0.70, 0.40)))
        a.oeil("oeil_" + nom, p + n * 0.005, n, 0.0280)
        a.piece("lourde_" + nom, K.paupiere(0.0280, 0.62), tuple(ROUX), mat=A.cadre(p + n * 0.008, n, H3 @ Vector((0, 0, 1))), poil=False)   # un simple ourlet en haut : l'œil reste ouvert
        po = A.profil([(0, 0), (0.037, 0.011), (0.058, 0.068), (0.058, 0.135), (0.041, 0.203), (0.017, 0.254), (0, 0.270)], 6)
        vers = (H3 @ Vector((c * 0.40, 0.25, 0.88))).normalized()      # en V, un peu en arrière
        E = A.cadre(H @ Vector((c * 0.065, 0.085, 0.095)) - vers * 0.030, vers, H3 @ Vector((c * 0.20, -0.95, 0.10)))   # le +Y du repère : vers l'avant
        oreille = A.tour(po, 36).etire(1.0, 0.30, 1.0)
        oreille.teinte = np.where((oreille.v[:, 2] > 0.222)[:, None], BRUN, ROUX)
        a.piece("oreille_" + nom, oreille, None, mat=E)
        a.piece("dedans_" + nom, A.tour(po, 28).etire(0.62, 0.30, 0.72).pose((0, 0.010, 0.022)), tuple(CLAIR), mat=E, poil=False)

    # ----- les bras : petits et repliés devant la poitrine, les mains brunes tombantes -----
    for nom, c in (("G", 1), ("D", -1)):
        chemin = [(c * 0.120, -0.200, 0.800), (c * 0.170, -0.275, 0.690), (c * 0.115, -0.395, 0.675)]
        a.piece("bras_" + nom, A.tube(A.courbe(propres(chemin), 6), lambda t: 0.046 - 0.010 * t, 14), tuple(ROUX))
        a.piece("main_" + nom, A.boule(1.0, 24, 12).sculpte(lambda v: K.bosse(v, (0, -0.4, -0.9), 0.15, 0.4)).etire(0.034, 0.036, 0.042),
                tuple(BRUN), pos=(c * 0.105, -0.420, 0.640), rot=(25, 0, 0))

    # ----- les pattes arrière : deux énormes cuisses, une jambe courte, de très longs pieds posés à plat devant -----
    for nom, c in (("G", 1), ("D", -1)):
        cuisse = A.boule(1.0, 40, 20).sculpte(lambda v: K.bosse(v, (0, 0.6, 0.5), 0.10, 0.5))       # la croupe ronde derrière
        a.piece("cuisse_arriere_" + nom, cuisse.etire(0.115, 0.215, 0.175), tuple(ROUX), pos=(c * 0.155, 0.000, 0.360), rot=(22, 0, c * 5))
        jambe = [(c * 0.175, -0.165, 0.270), (c * 0.185, -0.125, 0.160), (c * 0.195, -0.085, 0.080)]
        a.piece("jambe_arriere_" + nom, A.tube(A.courbe(propres(jambe), 6), lambda t: 0.062 - 0.012 * t, 16), tuple(ROUX))

        def pied(v):
            s = v * [0.072, 0.250, 0.048]
            s[:, 2] *= 1 + 0.35 * K.lisse((v[:, 1] + 0.2) / 0.9)          # le talon plus haut que les orteils
            s[:, 0] *= 1 - 0.22 * K.lisse(-v[:, 1])                        # les orteils plus étroits
            s[:, 2] = np.where(v[:, 2] < 0, s[:, 2] * 0.75, s[:, 2])        # la plante plus plate, posée
            return s
        p_ = A.boule(1.0, 36, 18)
        p_.teinte = np.where((p_.v[:, 1] < -0.70)[:, None], BRUN, ROUX)
        a.piece("pied_arriere_" + nom, p_.sculpte(pied), None, pos=(c * 0.200, -0.300, 0.040), rot=(0, 0, c * 6))

    # ----- la queue : longue et épaisse, elle descend de la croupe et se couche au sol derrière lui (le trépied) -----
    chemin = [(0.0, 0.100, 0.400), (0.0, 0.200, 0.270), (0.0, 0.300, 0.130), (0.0, 0.420, 0.080), (0.0, 0.620, 0.062), (0.0, 0.840, 0.045)]

    def rayon(t):
        r = 0.120 - 0.078 * t
        if t > 0.92:                                                        # le bout s'arrondit, jamais coupé net
            r *= math.sqrt(max(0.0, 1.0 - ((t - 0.92) / 0.08) ** 2))
        return max(r, 0.002)
    a.piece("queue", K.tube_peint(A.courbe(propres(chemin), 8), rayon, [(0.88, tuple(ROUX)), (1.0, tuple(BRUN))], 20), None)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")

if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("kangourou", styles.style_de("kangourou"), sys.modules[__name__]), "Kangourou")
