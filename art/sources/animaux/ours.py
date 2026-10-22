"""L'ours en peluche, quatrième dessin (16/10, planches 19-20 : « manque de réalisme ») : l'ours brun des sapins à QUATRE
PATTES, d'après les vues d'un modèle de référence (references_3d/ours, CC-BY : vues seulement, rien d'importé). Noisette
cendré, une longue masse posée sur quatre piliers ; la bosse de muscle au-dessus des épaules, plus haute que la croupe ;
la tête portée bas, devant, au museau allongé plus clair et au gros nez noir ; les petites oreilles rondes plantées sur
les coins du crâne ; de petits yeux calmes ; des pattes épaisses, sombres, aux griffes pâles ; un moignon de queue.
Il marche, la tête un peu tournée vers nous.

    python ours.py        fabrique la fiche art/apercus/animaux/ours.png (style du palier : B, peluche de magasin)
    (1er dessin : « le nounours de supermarché » ; 2e : « très géométrique » ; 3e : debout, un bras levé, refusé le 16/10 ;
    4e, 19/10 : « les oreilles horribles, et les pattes aussi » : petites oreilles rondes haut sur le crâne, colonnes
    épaisses sur de gros pieds plats à cinq doigts et griffes courtes ; la truffe plate et mate est gardée)
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

GONFLAGE = True                               # la base aux volumes de l'Artiste (fusion + gonflage), validée le 15/10

NOISETTE = np.array(M.hexa("#7a5c46"))        # la dominante (registre : brun noisette cendré #6e5846), un peu plus chaud (style B)
CLAIR = np.array(M.hexa("#a88c70"))           # le museau, le givre de la bosse
SOMBRE = np.array(M.hexa("#5a4435"))          # les pattes
GRIFFE = (0.82, 0.76, 0.66)                   # couleur de corne (19/10 : plus des dents blanches)
NEZ = M.hexa("#16110e")
FIL = M.hexa("#2a1c14")
H = Vector((0.0, -0.640, 0.505))              # le centre du crâne


def construire():
    a = K.Animal("ours")
    a.taille = 2.20

    # ----- le corps : une longue masse, la bosse au-dessus des épaules (le garrot), la croupe un peu plus basse ; le dos
    #       givré sur la bosse, le ventre un ton plus sombre -----
    def peint(m, L):
        ang = np.abs(np.arctan2(m.v[:, 0], m.v[:, 1]))              # 0 : le dos ; pi : le ventre
        f = m.v[:, 2] / L
        t = np.tile(NOISETTE, (len(ang), 1))
        t[ang > 2.30] = NOISETTE * 0.86
        t[(ang < 0.75) & (f > 0.62) & (f < 0.92)] = NOISETTE * 0.62 + CLAIR * 0.38    # le givre de la bosse
        return t
    rayon = O.interp([(0.0, 0.0), (0.04, 0.140), (0.15, 0.205), (0.40, 0.222), (0.66, 0.232), (0.83, 0.228), (0.94, 0.195), (1.0, 0.085)])
    O.corps_h(a, "corps", (0.0, 0.400, 0.440), 0.860, rayon, peint, None, cotes=56, pitch=4.0,
              deforme=O.gabarit(poitrail=0.06, taille=0.04, croupe=0.05, garrot=0.16, ventre=0.04, pos_poitrail=0.80))

    # ----- le cou épais, la tête portée bas devant le poitrail -----
    cou = O.tube_r([(0.0, -0.380, 0.540), (0.0, -0.480, 0.530), (0.0, -0.575, 0.510)], [0.170, 0.150, 0.128], 24)
    a.piece("cou", O.teinte(cou, NOISETTE), None)
    RT = A.repere(H, (8, 0, 16))                                   # le nez un peu bas, la tête tournée vers nous
    R3 = RT.to_3x3()
    crane = A.boule(1.0, 52, 26).sculpte(lambda v: K.emousse(v, 0.80))
    for c in (1, -1):
        crane.sculpte(lambda v, c=c: K.bosse(v, (c * 0.9, -0.2, -0.25), 0.22, 0.26))   # les bajoues
    a.piece("tete", O.teinte(crane.etire(0.132, 0.140, 0.118), NOISETTE), None, mat=RT)
    # le museau : allongé, qui s'affine, plus clair ; le gros nez noir au bout
    museau = A.tour(A.profil([(0.074, 0.0), (0.072, 0.040), (0.064, 0.090), (0.054, 0.130), (0.042, 0.160), (0, 0.170)], 5), 36)
    museau.etire(1.0, 0.86, 1.0)
    a.piece("museau", O.teinte(museau, CLAIR), None, mat=RT @ A.cadre(Vector((0.0, -0.080, -0.040)), (0.0, -1.0, -0.16), (0, 0, 1)))
    bout = RT @ Vector((0.0, -0.080 - 0.155, -0.040 - 0.025))
    # la truffe (16/10, 5e passage : la bille noire vernie se lisait comme une perle collée) : une vraie truffe d'ours,
    # plus petite, large et aplatie (plus large que haute, un peu plus large en haut), presque mate (feutrine), deux
    # narines devant ; et dessous, la petite bouche cousue : le sillon sous la truffe, puis deux courts traits
    def truffe(v):
        s_ = K.emousse(v, 0.80)
        s_[:, 0] *= 1.0 + 0.15 * v[:, 2]
        return s_
    NZ = (0.0, -0.245, -0.053)                                     # dans la tête (RT) : au bout du museau
    a.piece("nez", A.boule(1.0, 28, 14).sculpte(truffe).etire(0.030, 0.020, 0.018), NEZ, mat=RT @ A.repere(NZ), poil=False)
    for nom_n, c in (("G", 1), ("D", -1)):
        a.piece("narine_" + nom_n, A.boule(1.0, 14, 7).etire(0.0065, 0.0040, 0.0048), M.hexa("#050404"),
                mat=RT @ A.repere((c * 0.0120, NZ[1] - 0.0185, NZ[2] - 0.0010)), poil=False)
    centre_b = Vector((0.0, -0.170, -0.065))
    def vers(*t):
        return [tuple(Vector(q) - centre_b) for q in t]
    O.broder(a, "bouche", "museau", RT @ centre_b, vers((0.0, -0.243, -0.072), (0.0, -0.238, -0.083), (0.0, -0.235, -0.092)),
             0.0025, FIL, decolle=0.002, R=RT)
    for nom_b, c in (("G", 1), ("D", -1)):
        O.broder(a, "bouche_" + nom_b, "museau", RT @ centre_b,
                 vers((0.0, -0.235, -0.092), (c * 0.013, -0.231, -0.097), (c * 0.024, -0.222, -0.094)), 0.0025, FIL, decolle=0.002, R=RT)
    # les yeux : petits, rapprochés, à la racine du museau
    O.paire_yeux(a, "tete", H, (0.50, -0.80, 0.34), 0.0175, decolle=0.002, R=RT)
    # les oreilles (19/10, l'auteur : « les oreilles horribles ») : PETITES et RONDES, posées HAUT sur le crâne, un peu en
    # arrière des yeux, bien écartées l'une de l'autre (un écart d'une oreille entre elles), comme celles du modèle de
    # référence. Un demi-disque épais dont le bas entre dans le crâne et suit sa courbe, le creux tourné vers l'avant.
    # (18/10 : grandes, 12 cm sur un crâne de 26, et renforcées par le gonflage, elles faisaient deux champignons collés au
    # front : le gonflage ne renforce plus les parties fines de l'ours, voir gonflage_reglages plus bas)
    def oreille_f(v):
        s = v.copy()
        s[:, 1] += 0.45 * v[:, 0] ** 2                        # les bords viennent devant : le creux regarde vers l'avant
        s[:, 2] -= 0.30 * v[:, 0] ** 2                        # le bas des côtés suit la courbe du crâne
        return s
    for nom, c in (("G", 1), ("D", -1)):
        pos, n = a.surface("tete", H, R3 @ Vector((c * 0.56, 0.10, 0.82)))          # le haut du crâne, sur ses coins
        ore = A.boule(1.0, 28, 14).sculpte(oreille_f).etire(0.034, 0.017, 0.044)
        a.piece("oreille_" + nom, O.teinte(ore, NOISETTE * 0.85), None,
                mat=A.cadre(pos + n * 0.006, n, R3 @ Vector((0.0, -1.0, 0.0))))   # épaisseur d'avant en arrière
    a.tete = RT @ Vector((0.0, -0.250, -0.020))

    # ----- les pattes (19/10, l'auteur : « les pattes aussi, y'a pas d'effort ») : de vraies pattes d'ours, comme celles du
    #       modèle de référence. Des COLONNES larges, presque droites, à peine plus fines au poignet (18/10 : un tube de cheval
    #       de 9 cm au bas, sur un coussin rond de 19 cm, qui se lisait comme un bâton planté dans un chausson) ; la cuisse
    #       forte derrière ; de GROS PIEDS PLATS, la semelle au sol, plus larges que la colonne, cinq doigts ronds devant ;
    #       le pied arrière long (l'ours marche sur toute la plante) ; cinq griffes COURTES, couleur de corne, au bout des
    #       doigts. Le bas des pattes plus sombre, en poil. -----
    def pied_ours(dim, long_av):
        """Un gros pied plat : la semelle à plat, le dessus bombé qui descend vers les doigts, cinq doigts ronds sur le
        bord de devant. Le repère : le centre du pied au sol, -Y devant. Rend (maille, positions et directions des griffes)."""
        def plante(v):
            s = K.emousse(v, 0.80)
            s[:, 2] = np.maximum(s[:, 2], -0.62)                            # la semelle à plat
            s[:, 2] -= 0.22 * np.clip(-v[:, 1], 0.0, 1.0) * np.clip(s[:, 2] + 0.62, 0.0, 2.0) / 1.62   # plus mince vers les doigts
            return s
        m = A.boule(1.0, 40, 20).sculpte(plante).etire(*dim)
        m.v[:, 2] += 0.62 * dim[2]                                          # la semelle sur z = 0
        griffes_ = []
        for k in range(5):
            th = math.radians((k - 2) * 26.0)
            bord = Vector((math.sin(th) * dim[0] * 0.78, -math.cos(th) * dim[1] * 0.86, 0.0))
            doigt = A.boule(1.0, 18, 9).sculpte(lambda v: K.emousse(v, 0.85)).etire(0.029, 0.031 * long_av, 0.026)
            doigt.v += np.array([bord.x, bord.y, 0.024])
            m = m + doigt
            sens = Vector((math.sin(th) * 0.45, -math.cos(th), -0.55)).normalized()
            bout = bord + Vector((math.sin(th), -math.cos(th), 0.0)) * (0.026 * long_av)
            griffes_.append((Vector((bout.x, bout.y, 0.016)), sens))
        return m, griffes_

    for sgn, nom in ((1, "G"), (-1, "D")):
        for sorte, haut_, pied_, rayons, dim, recul, pl in (
                ("avant", (sgn * 0.140, -0.290, 0.440), (sgn * 0.148, -0.330, 0.060),
                 (0.118, 0.110, 0.102, 0.096, 0.092, 0.090, 0.090), (0.116, 0.132, 0.050), 0.30, 0.012),
                ("arriere", (sgn * 0.132, 0.250, 0.420), (sgn * 0.148, 0.270, 0.060),
                 (0.128, 0.122, 0.108, 0.098, 0.093, 0.090, 0.090), (0.116, 0.165, 0.050), 0.36, 0.020)):
            pts = O.points_jambe(haut_, pied_, "av" if sorte == "avant" else "ar", pl)
            a.piece("patte_%s_%s" % (sorte, nom), O.membre(pts, rayons, [(0.58, NOISETTE), (1.0, SOMBRE)], 28), None)
            fin = pts[-1]
            pied_m, griffes_ = pied_ours(dim, 1.0 if sorte == "avant" else 0.9)
            centre = Vector((fin[0], fin[1] - dim[1] * recul, 0.0))
            a.piece("pied_%s_%s" % (sorte, nom), O.teinte(pied_m, SOMBRE), None, pos=tuple(centre))
            for k, (q, sens) in enumerate(griffes_):
                g = O.couche(O.teinte(O.griffe(0.022, 0.0085), np.array(GRIFFE)), A.cadre(centre + q, sens, (0, 0, 1)))
                a.piece("griffe_%s_%s%d" % (sorte, nom, k), g, None, poil=False)
    for p in a._toutes():                                             # les pieds en poil, comme les jambes
        if p["nom"].startswith("pied_"):
            p["poil"], p["zone"] = "teinte", "poil"
    # (16/10, 4e passage : fondus et gonflés, les pieds plats devenaient des boules) : posés à part, larges et plats
    a.fusion_a_part = ("pied", "narine")
    # le gonflage sans renfort des parties fines : renforcées (jusqu'à 25 fois la pression), les oreilles sortaient de 11 cm
    # et faisaient des champignons (journal du 17/10 : « sorti jusqu'à 110 mm »)
    a.gonflage_reglages = {"fins": 0.0}

    # ----- la queue : un moignon rond derrière -----
    queue = A.boule(1.0, 20, 10).sculpte(lambda v: K.emousse(v, 0.9)).etire(0.050, 0.052, 0.048)
    a.piece("queue", O.teinte(queue, NOISETTE), None, pos=(0.0, 0.395, 0.560))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "quad")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("ours", styles.style_de("ours"), sys.modules[__name__]), "Ours")
