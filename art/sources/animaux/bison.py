"""Le bison en peluche (4e dessin, d'après la vache gardée par l'auteur : même tonneau, mêmes pattes fines, même tête et même
mufle, d'où il tient debout) : un brun tabac à l'arrière, toute la MASSE de l'avant d'un brun laine sombre, la grosse
BOSSE sur les épaules, la tête large et basse mais bien en vue, le mufle taupe, la barbe, le toupet de laine, deux cornes
courtes qui se relèvent, deux yeux grands ouverts de face. Il avance la tête basse, le regard par en dessous.

Les 5 traits de l'espèce (photos de Commons, 15/10) : 1. la grosse bosse sur les épaules et la croupe plus basse ; 2. toute
la laine épaisse et sombre de l'avant (tête, cou, épaules, jambes) contre l'arrière-train plus clair et ras ; 3. une grosse
tête large portée bas, le mufle large ; 4. deux cornes courtes et noires qui se recourbent vers le haut ; 5. une barbe sous
le menton, une queue fine à pinceau.

    python bison.py        fabrique la fiche art/apercus/animaux/bison.png
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import bpy  # avant mathutils
import numpy as np
from mathutils import Matrix, Vector

import atelier as A
import garnitures as G
import matieres as M
import outils_a as O
import peluche as K

CHARBON = M.hexa("#3b3c43")                 # les taches, les oreilles, le toupet, les sabots
TAUPE = M.hexa("#4a3d37")                   # le mufle : brun-gris sombre (plus de museau rose de vache)
VIEUX_ROSE = M.hexa("#d6aaa4")              # le dedans des oreilles, le pis
CORPS = Vector((0.0, 0.06, 0.365))
TABAC = M.hexa("#9a6a48")                   # l'arrière-train : brun tabac roux
LAINE = M.hexa("#3e2a22")                   # la masse de l'avant : laine brune sombre
NOIRBR = M.hexa("#2e2420")                  # la tête, la barbe
CORNE = M.hexa("#2a2624")                   # les cornes
LARGE, LONG, HAUT = 0.150, 0.340, 0.150     # les demi-mesures du tonneau
NUQUE = Vector((0.0, -0.330, 0.410))     # l'arrière du crâne : plus bas que la bosse, devant elle
LACET, PIQUE, PENCHE = 24.0, 18.0, 0.0    # la tête basse, tournée vers la caméra (~25°) : les deux yeux se voient de face


def tache(rayon, a2, p2, a3, p3):
    """Le contour d'une tache : un rond cabossé (l'ouverture de la rustine dans chaque direction)."""
    return lambda th: rayon * (1 + a2 * math.cos(2 * th + p2) + a3 * math.cos(3 * th + p3))


def meche(pos, tourne):
    """Une mèche du toupet, couchée sur le front (dans le repère de la tête), tournée de quelques degrés."""
    return A.boule(1.0, 20, 10).etire(0.019, 0.017, 0.034).pose(pos, (0, tourne, 0))


def paupiere(r, coupe):
    """Une lourde paupière : un demi-dôme de feutrine qui coiffe le haut d'un bouton de rayon r.
    coupe : la hauteur de son bord au-dessus du milieu du bouton, en rayons (0 = l'œil à moitié fermé)."""
    def f(v):
        s = v * [1.30 * r, 1.30 * r, 0.62 * r]
        s[:, 1] = np.maximum(s[:, 1], coupe * r)
        return s
    return A.boule(1.0, 32, 16).sculpte(f)


def construire():
    a = K.Animal("bison")
    a.taille = 3.00
    a.poil_long = 0.048                       # un poil LONG sur toute la bête : la laine de la bosse et de l'avant

    # ----- le corps : un tonneau presque carré, la panse qui pend, les os des hanches qui pointent -----
    def tonneau(v):
        for cote in (1, -1):
            v = K.bosse(v, (cote * 0.55, 0.60, 0.58), 0.13, 0.07)         # les deux os des hanches
        y = np.clip(v[:, 1], -1.0, 1.0)
        rond = np.sqrt(np.maximum(1 - y * y, 1e-9))
        k = np.maximum(1 - np.abs(y) ** 3.0, 0.0) ** (1 / 3.0) / rond     # des flancs droits, deux bouts francs
        h = np.maximum(np.hypot(v[:, 0], v[:, 2]), 1e-9)
        k = k * (np.abs(v[:, 0] / h) ** 3.0 + np.abs(v[:, 2] / h) ** 3.0) ** (-1 / 3.0)   # la section : un carré aux coins ronds
        s = np.stack([v[:, 0] * k * LARGE, y * LONG, v[:, 2] * k * HAUT], axis=1)
        panse = np.exp(-((y - 0.10) / 0.60) ** 2)
        s[:, 2] *= np.where(v[:, 2] < 0, 1 + 0.20 * panse, 1.0)           # la panse pend au milieu
        s[:, 0] *= 1 + 0.06 * panse                                       # ... et déborde sur les côtés
        # la BOSSE des épaules, ajoutée sur la forme FINIE (une bosse posée avant la mise en carré se repliait en plaques dressées)
        s[:, 2] += 0.205 * np.exp(-((s[:, 1] + 0.120) / 0.200) ** 2) * np.exp(-(s[:, 0] / 0.140) ** 2) * np.clip(v[:, 2], 0.0, 1.0)
        s[:, 2] -= 0.060 * np.clip(s[:, 1] / 0.340, 0.0, 1.0) * np.clip(v[:, 2], 0.0, 1.0)            # la croupe plus basse que les épaules
        return s
    corps = A.boule(1.0, 56, 28).sculpte(tonneau)
    G.sillons(corps, [14], 0.005, 1.1)
    corps.teinte = np.where((corps.v[:, 1] < 0.02)[:, None], np.asarray(LAINE), np.asarray(TABAC))
    a.piece("corps", corps, None, pos=CORPS)

    # ----- la tête : un bloc court et large ; dans son repère, X la gauche, Y le front, Z vers le mufle -----
    l, p = math.radians(LACET), math.radians(PIQUE)
    nez = Vector((math.sin(l) * math.cos(p), -math.cos(l) * math.cos(p), -math.sin(p)))
    T = A.cadre(NUQUE, nez) @ Matrix.Rotation(math.radians(PENCHE), 4, "Z")
    T3 = T.to_3x3()
    a.tete = T @ Vector((0, 0.06, 0.150))
    tete = A.tour(A.profil([(0, 0), (0.072, 0.012), (0.100, 0.050), (0.104, 0.090), (0.092, 0.135), (0.082, 0.170),
                            (0.080, 0.200), (0, 0.216)], 6), 48).etire(1.0, 0.80, 1.0)
    G.sillons(tete, [12], 0.004, 1.1)
    a.piece("tete", tete, NOIRBR, mat=T)
    # (la couture du chanfrein est retirée : elle se lisait comme une cicatrice)

    # ----- le cou : un gros boudin court qui descend du garrot jusque derrière le crâne -----
    cou = A.courbe([CORPS + Vector((0, -0.150, 0.030)), CORPS + Vector((-0.005, -0.265, -0.025)), T @ Vector((0, -0.030, 0.035))], 8)
    a.piece("cou", A.tube(cou, lambda t: 0.115 - 0.027 * t, 20), LAINE)

    # ----- le mufle : un large tambour de feutrine rose, deux gros naseaux, et la mâchoire qui part de côté (elle rumine) -----
    mufle = T @ Vector((0, -0.004, 0.203))
    a.piece("mufle", A.boule(1.0, 40, 20).sculpte(lambda v: K.emousse(v, 0.75)).etire(0.090, 0.060, 0.044), TAUPE,
            mat=T @ A.repere((0, -0.004, 0.203)))
    a.piece("machoire", A.boule(1.0, 32, 16).etire(0.070, 0.040, 0.058), NOIRBR, mat=T @ A.repere((0.050, -0.052, 0.200)))
    a.piece("barbe", A.boule(1.0, 24, 12).etire(0.075, 0.065, 0.120), NOIRBR, mat=T @ A.repere((0, -0.080, 0.135)))
    for nom, c in (("naseau_G", 1), ("naseau_D", -1)):
        a.rustine(nom, "mufle", mufle, T3 @ Vector((c * 0.40, 0.55, 0.73)), lambda th: 0.24 * (1 + 0.28 * math.cos(2 * th)),
                  CHARBON, 0.0025, 0)
    bouche = [T3 @ Vector((0.9 * x, -0.50 + 0.10 * x * x - 0.06 * x, 0.78)) for x in np.linspace(-0.85, 0.85, 9)]    # un sourire, plus haut d'un côté
    a.broderie("bouche", a.trace("mufle", mufle, bouche, 0.004), 0.0026, CHARBON)

    # ----- les yeux : deux yeux vivants, grands ouverts, sur l'avant de la tête (visibles de face) -----
    # posés dans le repère de la TÊTE (tournée de 24°) : le miroir se fait dans la tête, plus d'œil qui flotte hors du crâne
    O.paire_yeux(a, "tete", T @ Vector((0, 0, 0.080)), (0.52, 0.55, 0.58), 0.030, decolle=0.010, R=T)

    # ----- les petites cornes crème, les oreilles charbon doublées de rose, et le toupet qui retombe sur le front -----
    def feuille(v):                                       # une oreille : ronde à l'attache, plus étroite au bout
        s = v.copy()
        s[:, 0] *= 1 - 0.40 * K.lisse((v[:, 2] - 0.1) / 0.9)
        return s
    for nom, c in (("G", 1), ("D", -1)):
        # une corne en lyre : elle part de côté, monte, et sa pointe se retourne vers l'avant ; crème, le bout charbon
        corne = A.courbe([T @ Vector((c * x, y, z)) for x, y, z in ((0.060, 0.050, -0.030), (0.105, 0.070, -0.040),
                                                                     (0.135, 0.095, -0.015), (0.133, 0.140, 0.035))], 6)
        a.piece("corne_" + nom, K.tube_peint(corne, lambda t: 0.026 * (1 - t) ** 0.7 + 0.005, [(9, CORNE)], 14), None, poil=False)
        tombe = (T3 @ Vector((c * 0.93, -0.20, 0.30))).normalized()
        E = A.cadre(T @ Vector((c * 0.088, -0.012, 0.048)) + tombe * 0.058, tombe, T3 @ Vector((0, 0.75, 0.65)))
        a.piece("oreille_" + nom, A.boule(1.0, 32, 16).sculpte(feuille).etire(0.034, 0.011, 0.066), CHARBON, mat=E)
        a.piece("dedans_" + nom, A.boule(1.0, 24, 12).sculpte(feuille).etire(0.022, 0.006, 0.048).pose((0, 0.0075, 0.002)),
                VIEUX_ROSE, mat=E, poil=False)
    # le toupet : UNE seule masse de laine sur le front (plus de grappes de petites boules)
    a.piece("toupet", A.boule(1.0, 28, 14).etire(0.090, 0.075, 0.100), LAINE, mat=T @ A.repere((0, 0.070, 0.020)))
    # (la toison de boules est retirée : la bosse est d'un seul tenant, couverte d'un poil long)

    # ----- quatre pattes fines, le genou noueux, le sabot en feutrine charbon ; elles sont posées en quinconce
    #       (une vache au repos ne se tient jamais d'équerre, et vues de trois quarts elles ne se cachent pas l'une l'autre) -----
    pp = A.profil([(0.026, 0.040), (0.024, 0.085), (0.031, 0.120), (0.025, 0.155), (0.030, 0.21), (0.036, 0.26), (0, 0.29)], 6)
    ps = A.profil([(0, 0), (0.035, 0.004), (0.039, 0.024), (0.030, 0.050), (0, 0.054)], 5)
    for nom, x, y, rot in (("avant_G", 0.094, -0.160, (-6, -4, 0)), ("avant_D", -0.094, -0.105, (-2, 4, 0)),
                           ("arriere_G", 0.085, 0.215, (4, -4, 0)), ("arriere_D", -0.085, 0.275, (-3, 4, 0))):
        a.piece("patte_" + nom, A.tour(pp, 28), LAINE if nom.startswith("avant") else TABAC, pos=(x, y, 0.0), rot=rot)
        a.piece("sabot_" + nom, A.tour(ps, 28), CHARBON, pos=(x, y, 0.0), rot=rot, poil=False)

    # ----- la queue : une cordelette qui chasse les mouches vers sa gauche, un gros pompon charbon au bout -----
    queue = A.courbe([(0, 0.29, 0.45), (0, 0.345, 0.455), (0.02, 0.38, 0.41), (0.07, 0.39, 0.33), (0.14, 0.365, 0.28),
                      (0.195, 0.32, 0.275)], 8)
    a.piece("queue", A.tube(queue, 0.016, 12), TABAC)
    a.piece("pompon", A.boule(1.0, 28, 14).etire(0.042, 0.042, 0.048), CHARBON, pos=(0.214, 0.302, 0.282), rot=A.viser((0.6, -0.6, 0.3)))
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("bison", styles.style_de("bison"), sys.modules[__name__]), "Bison")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py bison). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.282                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.155, 0.446)),
    ('cou', 'corps', (-0.016, -0.049, 0.319)),
    ('tete', 'cou', (0.023, -0.318, 0.375)),
    ('oreille_G', 'tete', (0.095, -0.339, 0.378)),
    ('patte_av_G', 'corps', (0.075, -0.132, 0.282)),
    ('patte_ar_G', 'corps', (0.067, 0.196, 0.283)),
    ('queue', 'corps', (-0.001, 0.290, 0.453)),
]

PORTEURS = [
    ('sabot_arriere', 'patte_ar', True), ('patte_arriere', 'patte_ar', True), ('patte_avant', 'patte_av', True),
    ('sabot_avant', 'patte_av', True), ('oeil_reflet', 'tete'), ('machoire', 'corps'), ('oreille', 'oreille', True),
    ('toupet', 'corps'), ('naseau', 'tete'), ('pompon', 'corps'), ('dedans', 'oreille', True), ('bouche', 'tete'),
    ('corps', 'corps'), ('corne', 'tete'), ('barbe', 'tete'), ('mufle', 'corps'), ('queue', 'queue'),
    ('tete', 'tete'), ('oeil', 'tete'), ('cou', 'cou'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
    ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('cou', rot=(2 * r, 0, 8 * g - 6 * d))
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
    p.add('cou', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('tete', rot=(3 - 2 * onde(t, 2, -0.2), -2 * c, -2 * s))
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
    p.add('cou', rot=(34 * bas + 4 * coups, 0, 5 * leve))
    p.add('tete', rot=(18 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.085 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('cou', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.paire('oreille', rot=(-20 * vol, 0, 0))
    p.add('queue', rot=(-16 * vol, 0, -22 * fouet))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.155), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
