"""La baudroie des abysses en peluche, refaite le 19/10 d'après les VUES de son modèle 3D (jamais d'après l'anatomie) : un corps
aubergine sombre en coin, haut et large derrière la tête, qui s'effile en un pédoncule court et finit en une caudale évasée ;
une énorme gueule qui prend tout le devant (un creux sombre, des lèvres claires), des crocs d'ivoire LONGS plantés dans la
lèvre du haut, une rangée de petites dents sur la lèvre du bas ; un petit œil rond sur le côté de la tête ; deux nageoires
pectorales en palettes évasées de chaque côté ; et, du front, une longue canne qui monte puis retombe en arc devant le museau
et porte au bout la lanterne jaune citron.

    python baudroie_des_abysses.py        fabrique la fiche art/apercus/animaux/baudroie_des_abysses.png (style du palier : B)

Repère : l'avant est -Y, la queue +Y, le haut +Z. Les mesures viennent des vues (0°, 90°, 180°, 270°) : la longueur du museau à la
caudale vaut 1,0 ; la tête est la moitié du corps, plus haute (0,58) que large (0,54) ; la canne monte à 0,90 et sa lanterne
pend à 0,60, juste devant le museau.
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

AUBERGINE = np.array(M.hexa("#4a3248"))       # la dominante (registre : aubergine sombre) ; le style B éclaircit un peu
GRIS = np.array(M.hexa("#7b6a7a"))            # le dessous, les nageoires
CITRON = M.hexa("#fff04a")                    # l'accent : la lanterne
DENT = M.hexa("#fbf7ea")
BOUCHE = np.array(M.hexa("#241522"))          # l'intérieur de la gueule
LEVRE = np.array(M.hexa("#85708a"))           # le bord des lèvres, bien plus clair que le poil sombre : il dessine la gueule


# ----------------------------------------------------------------------- le corps : un seul volume, de la queue au museau
# (y, centre z, demi-hauteur au-dessus, demi-hauteur en dessous, demi-largeur) lus sur les vues de profil et de face
STATIONS = [
    (0.47, 0.230, 0.048, 0.048, 0.050),     # le bout du pédoncule (la caudale s'y plante)
    (0.44, 0.235, 0.052, 0.052, 0.054),
    (0.40, 0.255, 0.076, 0.078, 0.070),
    (0.32, 0.253, 0.097, 0.097, 0.105),
    (0.22, 0.255, 0.155, 0.155, 0.165),
    (0.10, 0.285, 0.248, 0.248, 0.240),
    (-0.04, 0.298, 0.285, 0.298, 0.270),    # le plus gros du corps, derrière la gueule
    (-0.19, 0.305, 0.258, 0.256, 0.258),
    (-0.30, 0.335, 0.212, 0.216, 0.242),
    (-0.37, 0.370, 0.172, 0.168, 0.228),
    (-0.42, 0.405, 0.122, 0.122, 0.185),    # le museau : plus bas que le front, la mâchoire en avance
]
Y_QUEUE, Y_NEZ = 0.47, -0.42

# la gueule : une ellipse sur le devant (centre, demi-largeur, demi-hauteur), creusée de PROFONDEUR vers l'arrière
ZM, AX, AZ, PROFONDEUR = 0.378, 0.230, 0.124, 0.250


def lisse(colonne, sigma=0.018):
    """Une courbe douce par les stations (interpolées puis lissées), rendue comme fonction de y."""
    ys = np.array([s[0] for s in STATIONS])[::-1]
    vs = np.array([s[colonne] for s in STATIONS])[::-1]
    g = np.linspace(-0.55, 0.55, 1101)
    c = np.interp(g, ys, vs)
    k = np.exp(-0.5 * (np.arange(-60, 61) * 0.001 / sigma) ** 2)
    k /= k.sum()
    p = np.concatenate([np.full(60, c[0]), c, np.full(60, c[-1])])
    c = np.convolve(p, k, mode="valid")
    return lambda y: np.interp(y, g, c)


ZC, HAUT, BAS, LARG = (lisse(i) for i in (1, 2, 3, 4))


def sm(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def corps_loft(cotes=96):
    """Le corps d'une pièce : des anneaux le long de Y, chacun une ellipse (haut et bas différents), un bout rond à chaque extrémité ;
    puis le creux de la gueule sur le devant, la peinture (dos aubergine, ventre gris, gueule sombre, lèvres claires)."""
    prof = []
    for t in np.linspace(0.0, math.pi / 2, 8):                         # le bout de la queue (h = -y : la queue en bas)
        prof.append((math.sin(t), -(Y_QUEUE + 0.022 * math.cos(t))))
    for s in np.linspace(Y_QUEUE, Y_NEZ, 126)[1:-1]:
        prof.append((1.0, -s))
    for t in np.linspace(0.0, math.pi / 2, 10):                        # le nez, arrondi
        prof.append((math.cos(t), -(Y_NEZ - 0.05 * math.sin(t))))
    m = A.tour(prof, cotes)

    X, Yr, H = m.v[:, 0], m.v[:, 1], m.v[:, 2]
    y = -H
    x = X * LARG(y)
    z = ZC(y) + np.where(Yr > 0, HAUT(y), BAS(y)) * Yr
    m.v = np.stack([x, y, z], axis=1)                                  # (X, Y, H) -> (x, -H, Y) : le sens des faces est gardé
    nrm = m.normales()
    avant = np.clip((-nrm[:, 1] - 0.05) / 0.25, 0.0, 1.0) * np.clip((-0.18 - y) / 0.10, 0.0, 1.0)   # ce qui regarde vers l'avant

    rho = np.sqrt((x / AX) ** 2 + ((z - ZM) / AZ) ** 2)
    creux = PROFONDEUR * np.clip(1.0 - rho ** 2, 0.0, None) ** 1.3 * avant
    m.v[:, 1] = y + creux

    # --- la peinture ---
    rel = (z - ZC(y)) / np.maximum(BAS(y), 1e-6)
    ventre = sm(-0.35, -0.70, rel)                                     # le dessous, gris
    base = AUBERGINE[None, :] * (1 - ventre[:, None]) + GRIS[None, :] * ventre[:, None]
    w_in = (1.0 - sm(0.76, 0.88, rho)) * avant
    w_le = sm(0.76, 0.88, rho) * (1.0 - sm(1.00, 1.22, rho)) * avant
    t = base * (1 - w_in - w_le)[:, None] + BOUCHE[None, :] * w_in[:, None] + LEVRE[None, :] * w_le[:, None]
    m.teinte = t
    return m


def croc(long, base, courbe):
    """Une dent : un cône effilé qui se courbe un peu (pied sur z = 0, pointe en z = long)."""
    m = O.pointe(long, base, 10)
    return m.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] + courbe * long * (v[:, 2] / long) ** 2, v[:, 2]], axis=1))


def construire():
    a = K.Animal("baudroie_des_abysses")
    a.taille = 1.00

    # ----- le corps -----
    corps = corps_loft()
    a.piece("corps", corps, None, pos=(0.0, 0.0, 0.0))
    V = corps.v

    # ----- les dents : plantées dans les lèvres (un sommet de la peau pour chaque racine), les longs crocs en haut -----
    def racine(xt, haut):
        zt = ZM + (AZ * 0.95 if haut else -AZ * 0.95) * math.sqrt(max(1.0 - (xt / AX) ** 2, 0.0))
        d = (V[:, 0] - xt) ** 2 + (V[:, 2] - zt) ** 2 + np.where(V[:, 1] < -0.10, 0.0, 9.0)
        i = int(np.argmin(d))
        return Vector(tuple(V[i]))

    # en haut : de longs crocs en désordre, entre des dents plus courtes (jamais une rangée régulière)
    pos_haut = [-0.185, -0.140, -0.092, -0.050, -0.004, 0.042, 0.088, 0.138, 0.182]
    long_haut = [0.070, 0.175, 0.100, 0.210, 0.085, 0.195, 0.115, 0.165, 0.075]
    for k, xt in enumerate(pos_haut):
        base = racine(float(xt), True)
        sens = Vector((-0.10 * xt / AX + 0.03 * (k % 3 - 1), -0.32 - 0.05 * (k % 2), -1.0)).normalized()
        ray_ = 0.0105 + 0.040 * long_haut[k]
        d = O.couche(croc(long_haut[k], ray_, -0.12), A.cadre(base - sens * 0.014, sens, (0, 1, 0)))
        a.piece("dent_haut%d" % k, d, DENT, poil=False)
    # en bas : une rangée de petites dents, inégales
    pos_bas = [-0.190, -0.152, -0.112, -0.074, -0.034, 0.008, 0.046, 0.086, 0.124, 0.160, 0.190]
    long_bas = [0.042, 0.062, 0.040, 0.070, 0.048, 0.036, 0.066, 0.044, 0.058, 0.038, 0.050]
    for k, xt in enumerate(pos_bas):
        base = racine(float(xt), False)
        sens = Vector((-0.08 * xt / AX, -0.26, 1.0)).normalized()
        d = O.couche(croc(long_bas[k], 0.0105 + 0.040 * long_bas[k], 0.10), A.cadre(base - sens * 0.012, sens, (0, 1, 0)))
        a.piece("dent_bas%d" % k, d, DENT, poil=False)

    # ----- la canne : elle part du dessus de la tête, monte presque droit puis retombe en arc devant le museau ; la lanterne au bout -----
    # (un arc régulier : la montée, puis un demi-ovale d'axe à y = -0,206, de demi-largeur 0,272 et de demi-hauteur 0,24, qui retombe devant le museau)
    chemin = [(0.0, 0.030, 0.490), (0.0, 0.048, 0.570), (0.0, 0.062, 0.640)]
    for th in np.linspace(0.0, math.radians(180.0), 13)[1:]:
        chemin.append((0.0, -0.206 + 0.272 * math.cos(th), 0.660 + 0.240 * math.sin(th)))
    chemin.append((0.0, chemin[-1][1], 0.625))
    rayons = [0.040, 0.034, 0.028] + list(np.linspace(0.024, 0.0125, 13)) + [0.0125]
    tige = O.tube_r(chemin, rayons, 14, 6)
    tige.teinte = np.tile(AUBERGINE * 0.92, (len(tige.v), 1))
    a.piece("tige", tige, None, poil=False)
    lant = A.boule(1.0, 32, 16).etire(0.036, 0.036, 0.056)
    a.piece("lanterne", lant, CITRON, pos=(0.0, -0.478, 0.596), poil=False)

    # ----- les yeux : petits, ronds, ouverts, sur le côté haut de la tête, tournés un peu vers l'avant -----
    O.paire_yeux(a, "corps", (0.0, -0.10, 0.30), (0.62, -0.40, 0.60), 0.040)

    # ----- les pectorales : des palettes évasées qui sortent des flancs, de chant vu de côté, au niveau du milieu de la tête -----
    palette = [(-0.050, -0.030), (0.0, -0.034), (0.050, -0.050), (0.110, -0.080), (0.170, -0.102), (0.215, -0.078), (0.235, -0.022),
               (0.235, 0.030), (0.215, 0.082), (0.170, 0.106), (0.110, 0.086), (0.050, 0.052), (0.0, 0.036), (-0.050, 0.030)]
    for nom, c in (("G", 1), ("D", -1)):
        feuille = O.nageoire(palette, 0.036, GRIS, 0.013)
        a.piece("pectorale_" + nom, O.couche(feuille, O.plan((c * 0.215, 0.035, 0.265), Vector((c * 1.0, 0.30, 0.18)), Vector((0.0, 0.0, 1.0)))),
                None, poil=False)

    # ----- la queue : le pédoncule est le bout du corps ; la caudale évasée s'y plante ; une petite dorsale pointe sur le dos -----
    caud = O.nageoire([(-0.030, -0.045), (0.0, -0.047), (0.035, -0.068), (0.075, -0.108), (0.108, -0.130), (0.126, -0.100), (0.131, -0.050),
                       (0.133, 0.0), (0.131, 0.050), (0.126, 0.100), (0.108, 0.130), (0.075, 0.108), (0.035, 0.068), (0.0, 0.047),
                       (-0.030, 0.045)], 0.040, GRIS * 0.9, 0.014)
    a.piece("caudale", O.couche(caud, O.plan_vertical((0.0, 0.452, 0.225), (0.0, 1.0, 0.0))), None, poil=False)
    dors = O.nageoire([(-0.025, -0.040), (-0.018, 0.020), (0.0, 0.050), (0.030, 0.072), (0.062, 0.084), (0.088, 0.066), (0.092, 0.030),
                       (0.092, -0.040)], 0.034, AUBERGINE * 1.15, 0.011)
    a.piece("dorsale", O.couche(dors, O.plan_dos((0.0, 0.350, 0.300))), None, poil=False)

    a.tete = Vector((0.0, -0.40, 0.38))
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("baudroie_des_abysses", styles.style_de("baudroie_des_abysses"), sys.modules[__name__]),
              "Baudroie des abysses")
