"""Le tapir en peluche de velours ras (3e dessin, 19/10, essai 2 : refait d'après son modèle 3D de référence, references_3d/tapir,
CC-BY, regardé en vues seulement ; rien n'en est importé). Les proportions relevées sur son profil (en unités du
modèle) : du bout de la trompe à la racine de la queue 5,4 ; le garrot à 3,45 ; le ventre à 1,2 du sol (des pattes
courtes, un tiers de la hauteur) ; un corps en TONNEAU presque aussi large que haut (1,8 sur 2,0), deux fois plus long que
haut ; une tête longue de 1,55 et haute de 1,25 à l'arrière, en coin : le front descend droit vers la trompe, le dessous
reste plat ; la trompe courte qui déborde la bouche et retombe jusqu'au niveau du menton ; de petites oreilles rondes
dressées à l'arrière du crâne ; un cou court et épais ; un moignon de queue. Les couleurs sont celles du registre
(COULEURS.md : ardoise bleutée, selle crème) : la référence est un « AI Tapir » brun-roux dont la tache claire du flanc
tombe à la place de la selle.

Les 5 traits de l'espèce (photos de Commons, 15/10 et 19/10) : 1. un gros corps en tonneau sur quatre pattes courtes et
épaisses, la croupe ronde ; 2. une tête en coin terminée par une petite TROMPE courte et mobile qui pend au-dessus de la
lèvre ; 3. de petites oreilles rondes et dressées, ourlées de blanc ; 4. de petits yeux sur les côtés de la tête ;
5. (tapir de Malaisie) l'avant et les pattes sombres, une grande selle claire du garrot à la croupe.

    python tapir.py        fabrique la fiche art/apercus/animaux/tapir.png (velours ras, palier 3)
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Vector

import atelier as A
import matieres as M
import outils_a as O
import peluche as K

GONFLAGE = True       # la base aux volumes gonflés de l'Artiste (fusion.py) : jointures fondues, bouts arrondis

ARDOISE = np.array(M.hexa("#7189ad"))         # la dominante : ardoise bleutée moyenne (le poil la fonce)
CREME = np.array(M.hexa("#fbf4e4"))           # l'accent : la selle, le bord des oreilles
SOMBRE = np.array(M.hexa("#4e5d7c"))          # le dedans des oreilles
TROMPE = np.array(M.hexa("#62769c"))          # la trompe et la lèvre : à peine plus sombres que la tête (pas de tache)
SABOT = M.hexa("#3a3a44")                     # les sabots, les narines

# les mesures, d'après le profil du modèle de référence (1 unité du modèle = 0,16 m ici ; la tête un peu plus grosse, peluche)
CORPS = Vector((0.0, 0.030, 0.355))           # le centre du tonneau
LARGE, LONG, HAUT = 0.150, 0.330, 0.165       # ses demi-mesures : large, long, haut
NUQUE = Vector((0.0, -0.272, 0.468))          # l'arrière du crâne
LACET, PIQUE = 12.0, 12.0                     # la tête un peu tournée vers la caméra de la fiche, le nez un peu bas
LT, R0 = 0.200, 0.092                         # la tête : sa longueur (sans la trompe) et son plus grand rayon
PROFIL_TETE = [(0, 0), (0.060, 0.006), (0.084, 0.024), (0.092, 0.050), (0.089, 0.080), (0.080, 0.110), (0.068, 0.140),
               (0.056, 0.165), (0.046, 0.185), (0.036, 0.198), (0, 0.205)]
PATTE_AV = [(0, 0), (0.034, 0.004), (0.037, 0.018), (0.031, 0.040), (0.028, 0.070), (0.031, 0.100), (0.037, 0.140),
            (0.043, 0.185), (0.047, 0.230), (0.048, 0.255), (0, 0.280)]
PATTE_AR = [(0, 0), (0.035, 0.004), (0.038, 0.018), (0.031, 0.040), (0.028, 0.068), (0.033, 0.100), (0.045, 0.145),
            (0.058, 0.190), (0.065, 0.235), (0.064, 0.260), (0, 0.285)]
PAS = 0.006


def cadre_tete():
    """Le repère de la tête : X sa gauche, Y le front, Z vers la trompe ; posé à la nuque."""
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    return A.cadre(NUQUE, nez)


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=40, pas=PAS):
    """Une pièce tournée le long de son axe (0 -> longueur), les deux bouts refermés en calotte ronde."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 5)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("tapir")
    a.taille = 2.00
    a.poil_long = 0.0050                       # le poil RAS du tapir : la selle crème se lit comme une robe plate

    # ----- le corps : un TONNEAU presque aussi large que haut, deux fois plus long que haut ; l'arrière (les cuisses) un peu
    #       plus gros que l'avant, le dos à peine voûté, la croupe ronde qui tombe vers la queue, le ventre un peu rond -----
    def tonneau(v):
        y = np.clip(v[:, 1], -1.0, 1.0)
        rond = np.sqrt(np.maximum(1 - y * y, 1e-9))
        k = np.maximum(1 - np.abs(y) ** 2.6, 0.0) ** (1 / 2.6) / rond        # des flancs pleins, deux bouts bien ronds
        s = np.stack([v[:, 0] * k * LARGE, y * LONG, v[:, 2] * k * HAUT], axis=1)
        gros = 1.0 + 0.07 * np.clip(y, 0.0, 1.0) - 0.05 * np.clip(-y, 0.0, 1.0)
        s[:, 0] *= gros
        s[:, 2] *= gros
        dessus, dessous = np.clip(v[:, 2], 0.0, 1.0), np.clip(-v[:, 2], 0.0, 1.0)
        s[:, 2] += dessus * (0.012 * np.exp(-((y + 0.10) / 0.45) ** 2) - 0.020 * np.clip(y - 0.45, 0.0, 1.0) / 0.55)
        s[:, 2] -= dessous * 0.014 * np.exp(-((y - 0.05) / 0.45) ** 2)                 # le ventre un peu rond
        return s
    corps = A.boule(1.0, 56, 28).sculpte(tonneau)
    # la selle : crème du garrot à la croupe, tout autour du corps ; la limite d'un trait net, juste derrière les épaules,
    # un peu penchée vers l'arrière en bas
    yb = -0.095 - 0.040 * (corps.v[:, 2] / HAUT) + 0.008 * np.sin(5.0 * np.arctan2(corps.v[:, 0], corps.v[:, 2]))
    corps.teinte = np.where((corps.v[:, 1] > yb)[:, None], CREME, ARDOISE)
    a.piece("corps", corps, None, pos=CORPS)

    # ----- le cou : court et épais, du garrot à l'arrière du crâne -----
    T = cadre_tete()
    T3 = T.to_3x3()
    cou = A.courbe([CORPS + Vector((0.0, -0.200, 0.060)), CORPS + Vector((0.0, -0.262, 0.095)), T @ Vector((0.0, -0.004, 0.040))], 8)
    a.piece("cou", A.tube(cou, lambda t: 0.112 - 0.022 * t, 24), tuple(ARDOISE))

    # ----- la tête en coin : le front descend droit vers la trompe, le dessous reste presque plat (les sections baissent à
    #       mesure qu'elles rétrécissent) ; un peu plus étroite que haute -----
    zs, rs = np.array([p[1] for p in PROFIL_TETE]), np.array([p[0] for p in PROFIL_TETE])

    def crane(v):
        r = np.interp(v[:, 2], zs, rs)
        v[:, 1] += 0.62 * (r - R0)
        v[:, 0] *= 0.86
        v[:, 1] -= 0.010 * np.exp(-((v[:, 2] - 0.035) / 0.040) ** 2) * (v[:, 1] < 0)   # la joue ronde, en bas à l'arrière
        return v
    tete = A.tour(A.profil(PROFIL_TETE, 6), 48).sculpte(crane)
    tete.peint(tuple(ARDOISE))
    a.piece("tete", tete, None, mat=T)
    a.tete = T @ Vector((0.0, 0.0, 0.120))

    # ----- la trompe : courte, épaisse, elle prolonge le nez, déborde la bouche et retombe en se recourbant un peu ;
    #       la lèvre du bas, plus courte, dessous -----
    fil = K.Fil([T @ Vector((0.0, -0.020, 0.160)), T @ Vector((0.0, -0.024, 0.205)), T @ Vector((0.0, -0.040, 0.238)),
                 T @ Vector((0.0, -0.064, 0.254))], T3 @ Vector((1.0, 0.0, 0.0)))
    trompe = fuseau([(0.0, 0.040), (0.35, 0.036), (0.70, 0.031), (0.92, 0.032), (1.0, 0.030)], fil.long, 36)
    a.piece("museau_trompe", trompe.sculpte(fil.couche), tuple(TROMPE))
    a.piece("machoire", A.boule(1.0, 28, 14).etire(0.040, 0.024, 0.046), tuple(TROMPE), mat=T @ A.repere((0.0, -0.064, 0.158)))
    bout, av, nq = fil.cadre(fil.long * 0.80)
    for nom, c in (("narine_G", 1), ("narine_D", -1)):
        axe = (Vector(av) * 0.55 - Vector(nq) * 0.75 + T3 @ Vector((c * 0.35, 0.0, 0.0))).normalized()
        a.rustine(nom, "museau_trompe", Vector(bout), axe, lambda th: 0.20 * (1 + 0.30 * math.cos(2 * th)), SABOT, 0.0022, 0)

    # ----- les petits yeux : sur les côtés de la tête, tournés vers l'avant (les deux se voient de face et de trois quarts) -----
    O.paire_yeux(a, "tete", T @ Vector((0.0, 0.000, 0.088)), (0.62, 0.18, 0.76), 0.021, decolle=0.005, R=T)

    # ----- les petites oreilles rondes, dressées à l'arrière du crâne : ardoise, ourlées de blanc par une doublure crème un
    #       peu plus grande posée derrière et plus haut (sa base ne touche pas la tête : rien de crème ne bave sur le crâne) ;
    #       le dedans sombre et creusé, remonté loin de la base (à l'essai 1, le creux perçait la peau au pied de l'oreille) -----
    def ovale(v):
        s = v.copy()
        s[:, 0] *= 1 - 0.18 * K.lisse((v[:, 2] - 0.2) / 0.8)
        return s
    for nom, c in (("G", 1), ("D", -1)):
        monte = (T3 @ Vector((c * 0.42, 0.88, -0.22))).normalized()
        E = A.cadre(T @ Vector((c * 0.050, 0.060, 0.026)) + monte * 0.030, monte, T3 @ Vector((c * 0.30, 0.10, 1.0)))
        a.piece("oreille_" + nom, A.boule(1.0, 32, 16).sculpte(ovale).etire(0.026, 0.013, 0.036), tuple(ARDOISE), mat=E)
        a.piece("bord_" + nom, A.boule(1.0, 32, 16).sculpte(ovale).etire(0.029, 0.009, 0.037).pose((0, -0.003, 0.008)),
                tuple(CREME), mat=E, poil=False)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).sculpte(ovale).etire(0.016, 0.005, 0.021).pose((0, 0.0075, 0.009)),
                tuple(SOMBRE), mat=E, poil=False)

    # ----- quatre pattes courtes et épaisses (les cuisses plus grosses derrière), posées en quinconce ; trois sabots ronds
    #       à l'avant de chaque pied -----
    for nom, x, y, profil, rot in (("av_G", 0.078, -0.205, PATTE_AV, (-4, -3, 0)), ("av_D", -0.078, -0.165, PATTE_AV, (-1, 3, 0)),
                                   ("ar_G", 0.082, 0.215, PATTE_AR, (5, -3, 0)), ("ar_D", -0.082, 0.255, PATTE_AR, (2, 3, 0))):
        cote = "_G" if nom.endswith("G") else "_D"
        a.piece("patte_" + nom, A.tour(A.profil(profil, 5), 32), tuple(ARDOISE), pos=(x, y, 0.0), rot=rot)
        for k in (-1, 0, 1):
            a.piece("sabot_%s%d%s" % (nom[:2], k + 1, cote), A.boule(1.0, 16, 8).etire(0.015, 0.019, 0.013), SABOT,
                    pos=(x + k * 0.022, y - 0.030 + abs(k) * 0.006, 0.012), poil=False)

    # ----- un moignon de queue, court et rond, sous la croupe -----
    a.piece("queue", A.boule(1.0, 20, 10).etire(0.020, 0.020, 0.032), tuple(CREME), pos=(0.0, 0.352, 0.405),
            rot=A.viser((0.0, 0.75, -0.66)))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("tapir", styles.style_de("tapir"), sys.modules[__name__]), "Tapir")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py tapir). Pivots d'après la géométrie de la fiche (19/10) : haut des pattes, base des
# oreilles, nuque, racine de la queue ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.280                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.030, 0.400)),
    ('cou', 'corps', (0.000, -0.200, 0.430)),
    ('tete', 'cou', (0.000, -0.272, 0.468)),
    ('oreille_G', 'tete', (0.054, -0.262, 0.528)),
    ('patte_av_G', 'corps', (0.078, -0.205, 0.270)),
    ('patte_ar_G', 'corps', (0.082, 0.215, 0.275)),
    ('queue', 'corps', (0.000, 0.345, 0.415)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('oeil', 'tete'), ('dedans', 'oreille', True), ('oreille', 'oreille', True),
    ('bord', 'oreille', True), ('museau', 'tete'), ('narine', 'tete'), ('machoire', 'tete'), ('tete', 'tete'), ('cou', 'cou'), ('corps', 'corps'),
    ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('sabot_av', 'patte_av', True),
    ('sabot_ar', 'patte_ar', True), ('queue', 'queue'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
    p.add('oreille_G', rot=(0, 0, 20 * cloche(t, 0.50, 0.05) - 8 * g))
    p.add('oreille_D', rot=(0, 0, -20 * cloche(t, 0.88, 0.05) + 6 * d))
    p.add('queue', rot=(0, 0, 10 * onde(t, 1)))
    p.ouvert = borne(1 - 0.3 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Sa marche : les pattes alternent, le corps oscille, la tête dodeline."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 26.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.paire('oreille', rot=(-8 + 3 * onde(t, 2, -0.25), 0, 0))
    p.add('queue', rot=(-6, 0, -10 * s))
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.paire('oreille', rot=(-6 * bas + 5 * leve, 0, 0))
    p.add('queue', rot=(0, 0, -7 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.162 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.296), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
