"""La taupe à nez étoilé en peluche : la petite brune de velours noir des galeries, trapue comme un rouleau, de grosses mains
roses en pelle brandies devant elle, pas d'oreilles, deux grains pour yeux, et au bout du museau l'étoile : vingt-deux
petits doigts roses qui rayonnent et tâtent tout ce qui passe, plus vite que l'œil ne voit. Elle trouve son repas en moins
d'une demi-seconde. Elle ne le regarde même pas : elle a le nez qui voit.

    python taupe_a_nez_etoile.py        fabrique la fiche art/apercus/animaux/taupe_a_nez_etoile.png (style du palier : C, velours ras)
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

VELOURS = np.array(M.hexa("#4a3d39"))         # la dominante (registre : brun noir velours #3a2f2c), un cran plus clair pour la lecture
DESSOUS = np.array(M.hexa("#5e504a"))         # le ventre
ROSE = np.array(M.hexa("#f0a0aa"))            # l'accent : l'étoile, les mains, les pieds, la queue
GRIFFE = np.array(M.hexa("#f2e6d6"))
NEZ = M.hexa("#241a18")
H = Vector((0.0, -0.480, 0.200))              # le centre de la tête


TOURNE = 25                                   # la fiche tourne la bête vers la caméra (25° devant) : on compte les DEUX yeux ; 0 pour le jeu


def construire():
    a = K.Animal("taupe_a_nez_etoile")
    a.taille = 0.58                                # plus gros : il se noyait dans l'herbe (« flou »)

    # ----- le corps : un rouleau trapu, les épaules fortes, le dos rond ; un cou presque nul -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))
        t = np.tile(VELOURS, (len(ang), 1))
        t[ang > 2.2] = DESSOUS
        return t
    rayon = O.interp([(0.0, 0.0), (0.05, 0.075), (0.20, 0.125), (0.50, 0.150), (0.78, 0.148), (0.93, 0.118), (1.0, 0.075)])
    # (16/10, planche 27) : un corps CYLINDRIQUE, sans épaules ni croupe sculptées (il faisait une patate bosselée)
    O.corps_h(a, "corps", (0.0, 0.34, 0.150), 0.74, rayon, peint, None, cotes=48, pitch=-3.0,
              deforme=O.gabarit(poitrail=0.0, taille=0.0, croupe=0.0, garrot=0.0, ventre=0.0))

    # ----- la tête : un cône court qui se prolonge en groin ; les yeux grains de poivre ; l'étoile rose au bout -----
    RT = A.repere(H, (6, 0, 12))
    tete = A.boule(1.0, 40, 20)
    tete.teinte = np.tile(VELOURS, (len(tete.v), 1))
    a.piece("tete", tete.etire(0.088, 0.118, 0.076), None, mat=RT)
    groin = A.boule(1.0, 28, 14).etire(0.044, 0.060, 0.040)
    a.piece("groin", O.teinte(groin, VELOURS * 0.96), None, mat=RT @ A.repere((0.0, -0.140, -0.010)))
    # l'étoile (16/10, planche 27 : une scie plate, illisible) : au bout du groin, un disque rose et ses deux narines, et
    # autour, en couronne, VINGT-DEUX doigts charnus au bout rond (onze de chaque côté, les deux du bas plus courts), qui
    # rayonnent et pointent un peu vers l'avant ; gardés à part (fondus, ils faisaient un disque)
    # (18/10, 4e essai : une marguerite plate) : l'étoile plus grande (presque la largeur de la tête), des doigts plus
    # épais au bout en massue, qui pointent nettement vers l'avant (une couronne en relief, pas une fleur posée à plat)
    a.piece("nez", A.boule(1.0, 24, 12).etire(0.033, 0.016, 0.033), tuple(ROSE * 0.95), mat=RT @ A.repere((0.0, -0.200, -0.008)), poil=False)
    for nom_n, c in (("G", 1), ("D", -1)):
        a.piece("narine_" + nom_n, A.boule(1.0, 12, 6).etire(0.0050, 0.0040, 0.0072), NEZ, mat=RT @ A.repere((c * 0.0105, -0.2155, -0.006)), poil=False)   # plus petites : un groin de cochon, sinon
    doigt = A.tour(A.profil([(0.0078, 0.0), (0.0080, 0.010), (0.0076, 0.024), (0.0068, 0.036), (0.0048, 0.044), (0.0, 0.0480)], 4), 12)
    etoile = None
    for k in range(22):
        th = 2.0 * math.pi * (k + 0.5) / 22 - math.pi / 2                     # le bas : th = -90 degrés, entre deux doigts
        bas = abs(math.sin(th) + 1.0) < 0.12                                  # les deux doigts du bas, plus courts
        dire = Vector((math.cos(th), -0.62, math.sin(th))).normalized()
        pos = Vector((0.0, -0.200, -0.008)) + Vector((math.cos(th) * 0.027, 0.0, math.sin(th) * 0.027))
        d = O.teinte(doigt.copie().etire(1.0, 1.0, 0.66 if bas else 1.0), ROSE)
        d = O.couche(d, RT @ A.cadre(pos, dire, (0, 1, 0)))
        etoile = d if etoile is None else etoile + d
    a.piece("etoile", etoile, None, poil=False)
    a.fusion_a_part = ("etoile", "narine", "main", "griffe")
    O.paire_yeux(a, "tete", H, (0.54, -0.76, 0.30), 0.0190, decolle=0.002, R=RT)

    # ----- les mains : de grosses pelles roses brandies devant, les cinq griffes claires dehors ; l'arrière : petits pieds roses -----
    for nom, c in (("G", 1), ("D", -1)):
        # (16/10, planche 27) : les mains en PELLES sont en bas, de chaque côté de la poitrine, la paume tournée vers
        # l'extérieur et vers l'arrière, comme pour creuser (levées à hauteur d'épaule, elles faisaient des ailes)
        bras = O.tube_r([(c * 0.110, -0.160, 0.170), (c * 0.170, -0.260, 0.120), (c * 0.205, -0.345, 0.095)], [0.072, 0.058, 0.046], 18)
        a.piece("bras_" + nom, O.teinte(bras, VELOURS), None)
        # (2e essai : petites et vues par la tranche) : PLUS GROSSES, la paume dehors et un peu vers l'avant (on la voit
        # de trois quarts)
        # (3e essai : vues par la tranche de face, elles restaient petites) : la paume tournée en avant et dehors, à 45°,
        # comme des rames prêtes à creuser : de face, on voit deux grandes pelles roses
        # (4e essai, 18/10 : à 45°, de face on les voyait encore de biais, en ovales) : la paume TOURNÉE EN AVANT (25° vers
        # dehors seulement), plus grandes, posées au sol de chaque côté de la tête ; les cinq griffes en éventail sur le
        # bord du dehors, pointées dehors et un peu en avant, comme des doigts écartés qui vont creuser
        paume = Vector((c * 0.42, -0.90, 0.05)).normalized()
        P_ = A.cadre(Vector((c * 0.218, -0.372, 0.100)), paume, (0, 0, 1))
        RX, RY = 0.098, 0.104
        pelle = A.boule(1.0, 32, 16).sculpte(lambda v: K.emousse(v, 0.75)).etire(RX, RY, 0.024)   # large et haute, plate
        # (6e et dernier essai, agent B, 19/10 : les ongles en cônes faisaient encore une rangée de pointes, une scie) : le bord
        # du dehors de la pelle devient CINQ DOIGTS ronds et serrés (un bord festonné : une main, plus un disque), et au bout de
        # chacun un ONGLE large, plat et arrondi comme une spatule, couleur ivoire : aucune pointe
        ANGLES = (-28.0, -14.0, 0.0, 14.0, 28.0)
        for ang in ANGLES:
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            doigt = A.boule(1.0, 16, 8).etire(0.012, 0.009, 0.022)              # en travers, dans l'épaisseur, vers le dehors
            pelle = pelle + O.couche(doigt, A.cadre(Vector((c * 0.86 * RX * ca, 0.86 * RY * sa, 0.0)), Vector((c * ca, sa, 0.0)), (0, 0, 1)))
        a.piece("main_" + nom, O.teinte(pelle, ROSE), None, mat=P_, poil=False)
        P3 = P_.to_3x3()
        for k, ang in enumerate(ANGLES):
            ca, sa = math.cos(math.radians(ang)), math.sin(math.radians(ang))
            base_g = P_ @ Vector((c * (0.86 * RX + 0.026) * ca, (0.86 * RY + 0.026) * sa, 0.0))   # au bout du doigt, un tiers dedans
            vers_g = P3 @ Vector((c * ca, sa, 0.15))                                             # dehors, un peu vers l'avant
            ongle = A.boule(1.0, 16, 8).etire(0.0095, 0.0035, 0.013)          # large, plat, au bout rond (une spatule)
            g = O.couche(O.teinte(ongle, GRIFFE), A.cadre(base_g, vers_g, P3 @ Vector((0.0, 0.0, 1.0))))
            a.piece("griffe_%s%d" % (nom, k), g, None, poil=False)
        cuisse = O.tube_r([(c * 0.120, 0.320, 0.170), (c * 0.140, 0.350, 0.100), (c * 0.135, 0.320, 0.040)], [0.085, 0.062, 0.042], 16)
        a.piece("cuisse_" + nom, O.teinte(cuisse, VELOURS), None)
        pied = A.boule(1.0, 24, 12).sculpte(lambda v: K.emousse(v, 0.8)).etire(0.040, 0.066, 0.016)
        a.piece("pied_" + nom, O.teinte(pied, ROSE), None, pos=(c * 0.135, 0.280, 0.017), rot=(0, 0, c * -10), poil=False)
    # ----- la queue : fine, du velours du corps, un peu courbée (16/10 : grasse et rose, elle faisait une saucisse) -----
    queue = K.tube_peint(A.courbe([(0.0, 0.390, 0.140), (0.0, 0.470, 0.115), (0.022, 0.540, 0.090), (0.040, 0.590, 0.080)], 5),
                         lambda t_: 0.016 - 0.007 * t_, [(1.0, tuple(VELOURS * 0.92))], 12)
    a.piece("queue", queue, None)
    a.tete = H + Vector((0.0, -0.20, 0.0))
    if TOURNE:
        O.tourner(a, TOURNE)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("taupe_a_nez_etoile", styles.style_de("taupe_a_nez_etoile"), sys.modules[__name__]), "Taupe à nez étoilé")
