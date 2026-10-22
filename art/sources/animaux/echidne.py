"""L'échidné en peluche (4e dessin, d'après le hérisson gardé par l'auteur : même galet rond, même manteau de piquants, mêmes
piquants de feutrine réunis en une pièce, mêmes petites pattes) : un brun prune, le manteau de piquants crème à pointe
sombre, la tête qui s'allonge en un LONG MUSEAU fin comme un tube, une petite truffe noire, deux petits yeux.

Les 5 traits de l'espèce (photos de Commons, 15/10) : 1. un petit corps rond et bas couvert de piquants ; 2. des piquants
crème à pointe sombre, serrés ; 3. un long museau fin en tube, sans oreilles visibles ; 4. de petits yeux ronds ; 5. de
fortes petites pattes aux griffes de fouisseur.

    python echidne.py        fabrique la fiche art/apercus/animaux/echidne.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import garnitures as G
import matieres as M
import peluche as K

PRUNE = M.hexa("#6e4c46")                     # la dominante : brun prune (le poil la fonce)
CREME = M.hexa("#fff2d0")                     # les piquants
POINTE = M.hexa("#5a4048")
FOURRURE = M.hexa("#4e3a2e")                  # le pelage brun entre les piquants (18/10)                    # le manteau, le bout du museau
BRUN_POINTE = M.hexa("#3e2a1e")               # la pointe sombre des piquants (16/10 ; plus foncée le 19/10, comme chez le vrai)
BEC = M.hexa("#4a4044")                       # le museau nu, gris ardoise sombre (19/10 : le tube rose-brun faisait une trompe)
GRIFFE_E = (0.80, 0.76, 0.70)

CORPS = Vector((0.0, 0.03, 0.072))
DOS = Vector((0.0, 0.15, 1.0)).normalized()        # l'axe du manteau de piquants : vers le haut, un peu vers l'arrière


def sur(a, piece, centre, vers):
    """Le point de la surface visé depuis « centre », et la normale à cet endroit."""
    p = a.trace(piece, centre, [vers], 0.0)[0]
    return p, a.trace(piece, centre, [vers], 1.0)[0] - p


def construire():
    a = K.Animal("echidne")
    a.taille = 0.50
    # (18/10, 8e essai : « le corps reste une boule violette, les piquants ne font qu'une collerette ») : une petite TÊTE à
    # part, devant ; derrière elle un dos en dôme allongé couvert de piquants de la nuque à la croupe, sur un pelage brun
    TETE_C = Vector((0.0, -0.118, 0.066))
    CORPS2 = CORPS + Vector((0.0, 0.030, 0.0))
    a.tete = TETE_C + Vector((0.0, -0.045, 0.020))

    def galet(v):
        s = v * [0.112, 0.150, 0.102]
        s[:, 2] *= 1 - 0.42 * K.lisse(-4 * v[:, 2])
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(galet), PRUNE, pos=CORPS2)
    a.piece("tete", A.boule(1.0, 40, 20).sculpte(lambda v: K.bosse(v, (0, -0.6, -0.4), 0.10, 0.40)).etire(0.060, 0.066, 0.056),
            PRUNE, pos=TETE_C)

    # ----- le manteau : une grande rustine chocolat qui laisse le visage dehors, ourlée de fil jaune -----
    e1 = DOS.cross(Vector((0, 0, 1))).normalized()
    e2 = DOS.cross(e1)

    def capuche(tour):                                    # tout le dessus et les flancs du dos, de la nuque à la croupe
        return 1.62

    def vers(angle, tour):                                # une direction à « angle » de l'axe du dos, en tournant autour
        return DOS * math.cos(angle) + (e1 * math.cos(tour) + e2 * math.sin(tour)) * math.sin(angle)
    a.rustine("manteau", "corps", CORPS2, DOS, capuche, FOURRURE, 0.004, feston=0)       # le pelage brun entre les piquants
    # (les vingt points blancs de l'ourlet du manteau sont retirés : entre les piquants, ils faisaient des bâtonnets, 16/10)

    # ----- le museau : un cône qui pointe le nez en l'air, la truffe en feutrine noire -----
    # (16/10, planche 21 : « je sais pas si c'est fait exprès ») : le museau faisait 0,32, plus long que le corps (0,26) ;
    # celui de l'échidné fait à peu près le tiers du corps, un tube court qui s'affine
    # (9e essai, 19/10 : à 0,19, le tube faisait les deux tiers du corps, une trompe ; celui de l'échidné à nez court en fait
    # le quart à peine) : 0,135, le tiers du corps et un peu plus d'une tête, sombre et nu, à peine courbé vers le bas
    LM = 0.135
    # (3e essai : fondu et gonflé avec le corps, il faisait une trompe épaisse : il reste à part, en feutrine lisse et nue comme
    # chez le vrai, et plus fin)
    museau = A.tour(A.profil([(0.025, 0.0), (0.0175, 0.018), (0.0135, 0.040), (0.0122, 0.075), (0.0110, 0.105), (0.0094, 0.124), (0, LM)], 6), 32)
    COURBE = 0.020                                        # le bout descend de 2 cm (gonflé, le tube s'épaissit : on le part fin)
    museau.sculpte(lambda v: v - np.outer(COURBE * np.clip(v[:, 2] / LM, 0.0, 1.0) ** 2, [0.0, 1.0, 0.0]))
    a.fusion_a_part = ("narine",)                         # le museau est fondu à la face (sans bord net) ; fin, il ne fait plus trompe
    NEZ = A.repere(TETE_C + Vector((0, -0.050, -0.006)), (96, 0, 0))   # dans ce repère : X la gauche, Y le haut, Z vers la truffe
    museau.teinte = np.where((museau.v[:, 2] > 0.80 * LM)[:, None], np.array(BEC) * 0.80, np.array(BEC))   # le bout plus sombre
    a.piece("museau", museau, None, mat=NEZ, poil=False)
    # (la couture du museau est retirée : le museau gardé à part, le fil flotterait)
    # (2e essai : plus de truffe en boule noire, « un nez de clown » : deux petites narines au bout du tube)
    for nom_n, c in (("G", 1), ("D", -1)):
        a.piece("narine_" + nom_n, A.boule(1.0, 12, 6).etire(0.0036, 0.0030, 0.0022), K.NOIR, mat=NEZ @ A.repere((c * 0.0034, 0.0010 - COURBE * 0.97, LM - 0.0025)), poil=False)
    # (la couture de bouche est retirée : le museau gardé à part, elle flottait dessous ; la bouche d'un échidné est une fente au bout)

    # ----- le visage : deux boutons sous le bord du manteau, deux joues pêche, deux petites oreilles -----
    # (9e essai : de trois quarts, l'œil du fond dépassait du bord de la tête comme un disque noir) : plus petits, un peu plus
    # devant, enfoncés dans le poil
    p, n = sur(a, "tete", TETE_C, (0.46, -0.78, 0.42))
    a.oeil("oeil", p + n * 0.002, n, 0.0155, paire=True)
    # (la joue cousue est retirée : son anneau jaune se lisait comme une boucle d'oreille)
    # (9e essai : les oreilles de l'échidné ne se voient presque pas ; les deux boutons au-dessus des yeux faisaient des
    # sourcils) : deux petites fentes à peine en relief, en arrière, cachées dans le poil
    p, n = sur(a, "tete", TETE_C, (0.80, 0.20, 0.45))
    oreille = p + n * 0.002
    O = A.cadre(oreille, n, (0, -1, 0.2))
    a.piece("oreille", A.boule(1.0, 24, 12).etire(0.010, 0.005, 0.010), PRUNE, mat=O, paire=True)
    a.rustine("pavillon", "oreille", oreille, O.to_3x3() @ Vector((0, 1, 0)), 1.0, PRUNE, 0.002, 0, paire=True)

    # ----- les piquants : des cônes de feutrine, le bout plus clair, tous réunis en une seule pièce -----
    # (16/10, 6e essai : « des cartes blanches plates en couronne », refusé par l'auteur) : des cônes ÉPAIS en obus, ronds (16
    # côtés), arrondis au bout, crème à pointe brune, serrés sur tout le dos, qui sortent du poil
    LP = 0.040
    cone = A.tour(A.profil([(0.0105, 0.0), (0.0104, 0.008), (0.0096, 0.018), (0.0078, 0.027), (0.0052, 0.034),
                            (0.0024, 0.0385), (0, LP)], 3), 16)
    t_ = np.clip((cone.v[:, 2] / LP - 0.52) / 0.22, 0.0, 1.0)
    t_ = t_ * t_ * (3 - 2 * t_)
    cone.teinte = np.array(CREME)[None, :] * (1 - t_[:, None]) + np.array(BRUN_POINTE)[None, :] * t_[:, None]
    hasard = np.random.default_rng(7)
    piquants, nombre = None, 1150                        # (520 : clairsemés ; serrés sur tout le dos)
    for i in range(nombre):                               # des directions bien réparties sur toute la boule ; on garde celles du manteau
        angle, tour = math.acos(1 - 2 * (i + 0.5) / nombre), i * 2.399963
        if angle > capuche(tour) - 0.09:
            continue
        p, n = sur(a, "corps", CORPS2, vers(angle, tour))
        if (p - TETE_C).length < 0.072:
            continue                                      # pas de piquant dans la tête
        devant = max(0.0, -float(n.y))                     # (7e essai : de face, ceux du bord faisaient une couronne de cartes
        pique = cone.copie().etire(1.0, 1.0, hasard.uniform(0.90, 1.15) * (1.0 - 0.45 * devant))   # autour de la tête) :
        pique.teinte = cone.teinte * hasard.uniform(0.93, 1.05)
        couche = (n + Vector((0, 0.32 + 1.5 * devant, 0.08)) + Vector(hasard.normal(0, 0.07, 3))).normalized()   # plus courts
        # devant et couchés vers l'arrière le long du corps : la face reste nue, les obus vont du front à la queue
        if p.z + couche.z * 0.05 < 0.008:
            continue                                      # celui-là piquerait le sol
        pique.pose(p - n * 0.004, A.viser(couche))       # le pied dans le poil
        piquants = pique if piquants is None else piquants + pique
    a.piece("piquants", piquants, None, poil=False)

    # ----- quatre petites pattes de fouisseur, brun sombre (9e essai : la feutrine rose faisait des pattes de cochon), trois
    #       griffes courtes et claires devant chacune -----
    def pied(v):
        s = v.copy()
        s[:, 1] -= 0.012 * K.lisse((0.03 - v[:, 2]) / 0.03)
        return s
    patte = A.tour(A.profil([(0, 0), (0.022, 0.003), (0.025, 0.016), (0.019, 0.034), (0.019, 0.06), (0, 0.072)], 5), 24).sculpte(pied)
    a.piece("patte_avant", patte, FOURRURE, pos=(0.062, -0.030, 0.0), poil=False, paire=True)
    a.piece("patte_arriere", patte, FOURRURE, pos=(0.070, 0.120, 0.0), poil=False, paire=True)
    ongle = A.tour(A.profil([(0.0042, 0.0), (0.0032, 0.005), (0.0018, 0.010), (0.0, 0.0145)], 3), 10)
    ongle.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] - 0.004 * (v[:, 2] / 0.0145) ** 2, v[:, 2]], axis=1))
    for sorte, (x0, y0) in (("avant", (0.062, -0.030)), ("arriere", (0.070, 0.120))):
        for k, dx in enumerate((-0.010, 0.0, 0.010)):
            sens = Vector((dx * 12.0, -1.0, -0.30)).normalized()
            a.piece("griffe_%s_%d" % (sorte, k), ongle.copie(), GRIFFE_E,
                    mat=A.cadre(Vector((x0 + dx, y0 - 0.033 + 0.004 * abs(dx) / 0.010, 0.009)), sens, (0, 0, 1)), poil=False, paire=True)
    return a


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py echidne)

from poses import Pose, borne, cloche, onde

OS = [
    ("racine", None, (0, 0, 0)),
    ("corps", "racine", (0, 0.05, 0.06)),             # l'avant du dos, avec la tête : le milieu du ventre (18/10, 8e essai)
    ("croupe", "corps", (0, 0.07, 0.06)),             # l'arrière du dos : il plie au même endroit, dans l'autre sens
    ("museau", "corps", (0, -0.168, 0.060)),          # la base du tube, devant la tête
    ("oreille_G", "corps", (0.050, -0.118, 0.100)),
    ("patte_avant_G", "corps", (0.062, -0.030, 0.058)),
    ("patte_arriere_G", "croupe", (0.070, 0.120, 0.058)),
]


def echine(points, cote):
    """Le galet est souple : le visage suit « corps », et le dos passe peu à peu à « croupe » vers l'arrière."""
    arriere = K.lisse((points[:, 1] + 0.01) / 0.14)
    return {"corps": 1.0 - arriere, "croupe": arriere}


# le galet et tout ce qui est cousu dessus plient ensemble, et se rangent avec « corps »
PORTEURS = [("corps", echine, "corps"), ("tete", echine, "corps"), ("manteau", echine, "corps"), ("ourlet", echine, "corps"), ("piquants", echine, "corps"),
            ("oeil", echine, "corps"), ("joue", echine, "corps"),
            ("museau", "museau"), ("truffe", "museau"), ("narine", "museau"), ("bouche", "museau"),
            ("oreille", "oreille", True), ("pavillon", "oreille", True),
            ("patte_avant", "patte_avant", True), ("patte_arriere", "patte_arriere", True),
            ("griffe_avant", "patte_avant", True), ("griffe_arriere", "patte_arriere", True)]


def repos(t):
    """Il respire, lève le nez pour flairer l'air, le museau qui frétille, jette un œil de côté, secoue une oreille."""
    p = Pose()
    r = onde(t, 2)
    flaire = cloche(t, 0.28, 0.16)                       # le nez en l'air
    cote = cloche(t, 0.72, 0.13)                         # un regard vers sa gauche, sans se déranger
    fremit = onde(t, 14) * (0.3 + 0.7 * flaire)          # le museau ne tient pas en place
    p.add("corps", rot=(-13 * flaire, 0, 9 * cote), ech=(1 + 0.012 * r, 1, 1 + 0.022 * r))
    p.add("croupe", rot=(12 * flaire, 0, -9 * cote))     # la croupe reste posée : elle rend au sol ce que l'avant a pris
    p.paire("patte_avant", rot=(13 * flaire, 0, 0), pos=(0, 0, -0.012 * flaire))
    p.add("museau", rot=(-9 * flaire + 4 * fremit, 0, 12 * cote))
    p.add("oreille_G", rot=(0, 28 * (cloche(t, 0.50, 0.025) + cloche(t, 0.56, 0.025)), 0))
    p.ouvert = 1 - cloche(t, 0.10, 0.02) - cloche(t, 0.63, 0.02)
    return p


def avance(t):
    """Il trottine : quatre petits pas pressés par boucle, en diagonale, la croupe qui chaloupe, le nez au ras du sol."""
    p = Pose()
    c, s = math.cos(2 * math.tau * t), math.sin(2 * math.tau * t)
    p.add("corps", pos=(0, 0, 0.003 + 0.006 * abs(s)), rot=(4 + 2 * onde(t, 1), 3 * c, 4 * s))
    p.add("croupe", rot=(-4, -5 * c, -8 * s))
    p.add("museau", rot=(8 + 5 * onde(t, 4), 0, 5 * onde(t, 1)))
    for nom, sens in (("patte_avant_G", 1), ("patte_arriere_D", 1), ("patte_avant_D", -1), ("patte_arriere_G", -1)):
        p.add(nom, rot=(34 * sens * s, 0, 0), pos=(0, 0, 0.018 * max(0.0, -sens * c) - 0.003))
    p.paire("oreille", rot=(-8 * abs(s), 0, 0))
    return p


def mange(t):
    """Le nez piqué dans l'herbe, il fouille par petits coups, puis relève la tête et mâche, le museau qui remue."""
    p = Pose()
    leve = cloche(t, 0.84, 0.14)
    bas = 1 - leve
    coups = max(0.0, onde(t, 5)) ** 2 * bas
    p.add("corps", rot=(13 * bas - 7 * leve + 3 * coups, 0, 5 * onde(t, 1) * bas))
    p.add("croupe", rot=(-11 * bas + 6 * leve, 0, -5 * onde(t, 1) * bas))
    p.paire("patte_avant", rot=(-13 * bas + 7 * leve, 0, 0), pos=(0, 0, 0.014 * bas - 0.007 * leve))
    p.add("museau", rot=(26 * bas + 6 * coups + 5 * onde(t, 10) * leve, 0, 0))
    return p


def joie(t):
    """Il se dresse sur ses pattes arrière, le nez au ciel, et trépigne des pattes avant en remuant la croupe : trois petits sauts."""
    p = Pose()
    u = borne(t / 0.9)
    env = math.sin(math.pi * u)
    saut = abs(math.sin(3 * math.pi * u)) * env
    p.add("corps", pos=(0, 0, 0.026 * env + 0.035 * saut), rot=(-28 * env, 0, 0))
    p.add("croupe", rot=(24 * env, 0, 12 * onde(u, 3) * env))
    p.add("museau", rot=(-10 * env + 5 * onde(u, 6) * env, 0, 0))
    p.add("patte_avant_G", rot=(-18 * env + 26 * onde(u, 6) * env, 0, 0))
    p.add("patte_avant_D", rot=(-18 * env - 26 * onde(u, 6) * env, 0, 0))
    p.paire("oreille", rot=(0, 18 * onde(u, 6) * env, 0))
    return p


def dort(t):
    """En boule : le dos rond, le nez rentré au ras du sol, les pattes cachées, il ne dépasse plus que des piquants."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add("corps", pos=(0, 0, 0.014), rot=(30, 0, 0), ech=(1.05 + 0.012 * r, 0.96, 1.03 + 0.025 * r))
    p.add("croupe", rot=(-58, 0, 0))                     # l'arrière s'enroule à son tour
    p.add("museau", rot=(14, 0, 0), ech=(0.8, 0.8, 0.8))
    p.paire("patte_avant", rot=(-45, 0, 0), pos=(0, 0.012, 0.030), ech=(0.7, 0.7, 0.7))
    p.paire("patte_arriere", rot=(45, 0, 0), pos=(0, -0.012, 0.030), ech=(0.7, 0.7, 0.7))
    p.paire("oreille", rot=(-25, 0, 0))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}


if __name__ == "__main__":
    K.planche(construire)
