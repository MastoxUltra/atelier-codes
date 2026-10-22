"""Le phacochère en peluche cousue main, REFAIT d'après le modèle 3D de référence (19/10, l'auteur : « refais-le à partir du
modèle 3D » ; silhouettes.py et vues de references_3d/phacochere, CC-BY : des proportions et des vues, rien n'est repris) :
un rouille franc, DEBOUT sur de longues pattes fines (il n'est plus à genoux), un long tonneau au dos droit, le ventre bas,
une GROSSE tête en coin portée plus bas que le garrot, le groin en disque plat large, deux grandes défenses recourbées
vers le haut, deux grosses verrues sous les yeux, de grandes oreilles pointues dressées, la crinière en crête de soies
raides du crâne jusqu'au milieu du dos, la queue fine dressée à houppe noire.

Les 5 traits de l'espèce (vues du modèle de référence, 19/10) : 1. un long corps bas à dos droit sur des pattes fines
(hauteur au garrot / longueur du tronc 0,8) ; 2. une très grosse tête en coin, aussi large que le tronc, portée basse ;
3. un groin plat et large, des défenses qui montent de chaque côté ; 4. des verrues en plaques sous les yeux et au museau ;
5. une crinière de longues soies de la nuque au milieu du dos, la queue fine dressée.

    python phacochere.py        fabrique la fiche art/apercus/animaux/phacochere.png (cousu main, palier 2)
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


ROUILLE = M.hexa("#d98a58")                   # la dominante : rouille franc (le poil le fonce : on le prend clair)
SOMBRE = M.hexa("#5a3a2c")                    # la crinière, le museau, la houppe
IVOIRE = M.hexa("#fff2d8")                    # l'accent : les défenses
CLAIR = M.hexa("#f2c8a0")                     # le dessous, le tour du museau
BASE = np.array(ROUILLE)
LACET = 24.0                                  # la tête tournée vers la caméra de la fiche
PAS = 0.010


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=72, pas=PAS):
    """Un fuseau (fraction, rayon) refermé en calotte aux deux bouts, à coucher le long d'un K.Fil."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("phacochere")
    a.taille = 1.00

    # ----- le tronc : un long tonneau d'une pièce, de la croupe au garrot (le dos droit, le garrot un peu plus haut, le ventre bas) -----
    chemin = [(0.0, 0.350, 0.372), (0.0, 0.200, 0.392), (0.0, 0.030, 0.402), (0.0, -0.150, 0.408), (0.0, -0.320, 0.418), (0.0, -0.470, 0.405)]
    fil = K.Fil(chemin, (1, 0, 0))
    L = fil.long
    bloc = fuseau([(0.0, 0.0), (0.03, 0.105), (0.12, 0.146), (0.30, 0.165), (0.55, 0.168), (0.76, 0.172), (0.90, 0.150), (0.97, 0.120), (1.0, 0.0)], L, 72)
    x, y, z = bloc.v[:, 0], bloc.v[:, 1], bloc.v[:, 2]
    f = z / L
    bloc.v[:, 0] *= 0.90                                                               # un tonneau un peu plus haut que large
    bloc.v[:, 1] += 0.018 * np.exp(-((f - 0.72) / 0.16) ** 2) * (y > 0)               # le garrot, à peine plus haut
    t = np.tile(BASE, (len(z), 1))
    t[(y < -0.075) & (np.abs(x) < 0.075)] = np.asarray(CLAIR)                          # le ventre clair
    bloc.teinte = t
    a.piece("bloc", bloc.sculpte(fil.couche), None)

    # la crinière : une crête de soies plates couchées vers l'arrière, plantées sur l'échine (du garrot au milieu du dos)
    rng = np.random.default_rng(6)
    for i, yy in enumerate(np.linspace(-0.40, 0.00, 17)):
        p, n = a.surface("bloc", Vector((0.0, yy, 1.0)), Vector((0.0, 0.0, -1.0)))
        h = 0.040 + 0.062 * float(np.exp(-((yy + 0.30) / 0.22) ** 2))
        a.piece("soie_%02d" % i, A.boule(1.0, 10, 6).etire(0.010, 0.016, h + 0.010 * rng.random()), SOMBRE,
                pos=(0.0, yy, p.z + 0.002), rot=(rng.uniform(-30, -12), 0, rng.uniform(-8, 8)), poil=False)

    # ----- la tête : une grosse tête en coin, aussi large que le tronc, portée plus bas que le garrot, tournée vers nous -----
    H = A.repere(Vector((0.0, -0.565, 0.372)), (-10, 0, LACET), (1.14, 1.14, 1.14))          # la tête du modèle 3D est ÉNORME : aussi large que le tronc
    H3 = H.to_3x3()

    def large(v):
        s = K.emousse(v, 0.80)
        s[:, 1] *= 0.82
        return s * [0.122, 0.196, 0.112]          # une face LONGUE et assez plate, une GROSSE tête
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(large), ROUILLE, mat=H @ A.repere((0, 0, 0)))
    a.piece("groin", A.boule(1.0, 32, 16).etire(0.088, 0.070, 0.050), tuple(np.asarray(ROUILLE) * 0.80), mat=H @ A.repere((0, -0.175, -0.026)))   # le groin : un DISQUE plat et large
    a.piece("nez", A.boule(1.0, 20, 10).etire(0.044, 0.022, 0.024), tuple(SOMBRE), mat=H @ A.repere((0, -0.232, -0.026)), poil=False)
    a.tete = H @ Vector((0, -0.130, -0.020))
    fw_ = H3 @ Vector((0, -1, 0))
    a.cap_tete = Vector((fw_.x, fw_.y, 0.0)).normalized()                  # le gros plan se place devant la tête tournée : les deux yeux se voient

    for nom, c in (("G", 1), ("D", -1)):
        # les yeux : petits mais ronds et ouverts, hauts sur la face ; sous chacun, une grosse verrue pâle
        p, n = a.surface("tete", H @ Vector((0, 0.0, 0.0)), H3 @ Vector((c * 0.62, -0.62, 0.50)))
        a.oeil("oeil_" + nom, p + n * 0.008, n, 0.0380)
        pw, nw = a.surface("tete", H @ Vector((0, 0.0, 0.0)), H3 @ Vector((c * 0.80, -0.50, -0.20)))
        a.piece("verrue_0" + nom, A.boule(1.0, 20, 10).etire(0.038, 0.038, 0.026), CLAIR,
                mat=A.cadre(pw - nw * 0.008, nw, H3 @ Vector((0, 0, 1))), poil=False)
        pv, nv = a.surface("tete", H @ Vector((0, 0.0, 0.0)), H3 @ Vector((c * 0.55, -0.84, -0.12)))
        a.piece("verrue_1" + nom, A.boule(1.0, 16, 8).etire(0.026, 0.026, 0.018), CLAIR,
                mat=A.cadre(pv - nv * 0.006, nv, H3 @ Vector((0, 0, 1))), poil=False)
        # les défenses : elles sortent au coin du groin et montent en se recourbant
        ch = [H @ Vector(q) for q in ((c * 0.080, -0.215, -0.034), (c * 0.120, -0.228, -0.016), (c * 0.150, -0.208, 0.030), (c * 0.160, -0.168, 0.078))]   # écartées vers l'EXTÉRIEUR : de face, elles ne passent plus devant l'œil (Cohérence 19/10)
        a.piece("defense_" + nom, A.tube(A.courbe(propres(ch), 6), lambda t: 0.017 - 0.012 * t, 14), IVOIRE, poil=False)
        # les grandes oreilles pointues, dressées derrière le front
        po = A.profil([(0, 0), (0.044, 0.012), (0.056, 0.060), (0.040, 0.112), (0.012, 0.146), (0, 0.160)], 6)
        E = A.cadre(H @ Vector((c * 0.086, 0.100, 0.082)), H3 @ Vector((c * 0.36, 0.14, 0.92)), H3 @ Vector((c * 0.3, -0.9, 0.0)))
        a.piece("oreille_" + nom, A.tour(po, 28).etire(1.0, 0.40, 1.0), ROUILLE, mat=E)
        a.piece("dedans_" + nom, A.tour(po, 24).etire(0.58, 0.30, 0.74).pose((0, 0.010, 0.012)), CLAIR, mat=E, poil=False)

    # ----- les pattes : droites et FINES (les vraies pattes du modèle 3D), l'avant gauche à peine en avant ; la queue fine, dressée -----
    def patte(pts, r0, r1):
        return A.tube(A.courbe(pts, 6), lambda t: r0 + (r1 - r0) * t, 14)
    for nom, c in (("av_G", 1), ("av_D", -1)):
        av = -0.012 if c > 0 else 0.0
        a.piece("patte_" + nom, patte([(c * 0.095, -0.300, 0.360), (c * 0.100, -0.292 + av, 0.200), (c * 0.100, -0.285 + av, 0.030)], 0.052, 0.028), ROUILLE)
        a.piece("sabot_" + nom, A.boule(1.0, 20, 10).etire(0.030, 0.044, 0.022), SOMBRE, pos=(c * 0.100, -0.292 + av, 0.022), poil=False)
    for nom, c in (("ar_G", 1), ("ar_D", -1)):
        a.piece("patte_" + nom, patte([(c * 0.100, 0.245, 0.350), (c * 0.108, 0.285, 0.170), (c * 0.104, 0.273, 0.030)], 0.060, 0.028), ROUILLE)
        a.piece("sabot_" + nom, A.boule(1.0, 20, 10).etire(0.032, 0.046, 0.022), SOMBRE, pos=(c * 0.104, 0.269, 0.022), poil=False)
    a.piece("queue", A.tube(A.courbe([(0.0, 0.343, 0.392), (0.0, 0.397, 0.500), (0.0, 0.415, 0.640)], 5), 0.012, 12), ROUILLE)
    a.piece("houppe", A.boule(1.0, 16, 8).etire(0.032, 0.032, 0.070), SOMBRE, pos=(0.0, 0.419, 0.700))
    import deformer_b as DF
    DF.etirer(a, sy=1.10, sz=1.08)                                  # plus haut sur pattes, un peu plus long (modèle 3D : dégagement du ventre 0,35 de la hauteur)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("phacochere", styles.style_de("phacochere"), sys.modules[__name__]), "Phacochère")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py phacochere). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.381                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.143, 0.542)),
    ('tete', 'corps', (-0.018, -0.442, 0.417)),
    ('oreille_G', 'tete', (0.030, -0.459, 0.496)),
    ('patte_av_G', 'corps', (0.102, -0.339, 0.386)),
    ('patte_ar_G', 'corps', (0.103, 0.283, 0.377)),
    ('queue', 'corps', (0.001, 0.370, 0.435)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('verrue_0G', 'corps'), ('verrue_1G', 'corps'), ('verrue_0D', 'corps'),
    ('verrue_1D', 'corps'), ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True),
    ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('soie_00', 'tete'), ('soie_01', 'tete'),
    ('soie_02', 'tete'), ('soie_03', 'tete'), ('soie_04', 'tete'), ('soie_05', 'tete'), ('soie_06', 'tete'),
    ('soie_07', 'tete'), ('soie_08', 'tete'), ('soie_09', 'tete'), ('soie_10', 'tete'), ('soie_11', 'tete'),
    ('soie_12', 'tete'), ('soie_13', 'tete'), ('soie_14', 'tete'), ('soie_15', 'tete'), ('soie_16', 'tete'),
    ('oreille', 'oreille', True), ('defense', 'tete'), ('houppe', 'corps'), ('dedans', 'oreille', True),
    ('queue', 'queue'), ('groin', 'corps'), ('bloc', 'corps'), ('tete', 'tete'), ('oeil', 'tete'), ('nez', 'tete'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.114 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.210), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
