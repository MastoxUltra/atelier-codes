"""Le poisson-lune en peluche : un énorme disque d'argent froid, nacré, qui n'est que tête : pas de queue, une frange
ondulante à la place, un aileron en haut et un autre dessous, deux grands comme des voiles. Debout sur la tranche, sur
son aileron du bas, il regarde de côté d'un œil rond sous une paupière à demi tombée, la petite bouche en « o » :
il a l'air de n'avoir rien pensé depuis sa naissance, et d'en être très content.

    python poisson_lune.py        fabrique la fiche art/apercus/animaux/poisson_lune.png (style du palier : B, peluche de magasin)
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

ARGENT = np.array(M.hexa("#b3bfd0"))          # la dominante (registre : argent bleuté, plus froid et nacré)
NACRE = np.array(M.hexa("#e7ecf4"))           # le ventre, les reflets
GRIS = np.array(M.hexa("#7f8a9e"))            # les nageoires, la frange
FIL = M.hexa("#3a4256")
TOURNE = -18                                  # trois quarts : le flanc du disque ET les deux yeux (à -30, l'œil du fond disparaissait, 18/10) ; 0 pour le jeu


def couche(m, mat):
    r = np.array(mat)
    m.v = m.v @ r[:3, :3].T + r[:3, 3]
    return m


def construire():
    a = K.Animal("poisson_lune")
    a.taille = 3.00

    # (16/10, passé à la session Art après six essais : le disque se lisait comme une tranche mince, un seul œil, des
    # ailerons en lames, pas de clavus) : un DISQUE de peluche, aussi haut que long, épais devant (le visage large, les deux
    # yeux se voient de trois quarts) et plus mince derrière ; deux grandes nageoires épaisses, haute et basse, rejetées
    # vers l'arrière comme chez la vraie môle ; et derrière, le CLAVUS : la queue tronquée, un bord ondulé en festons
    ZC = 0.700                                     # debout sur sa nageoire du bas
    # (18/10, 7e essai : un seul œil de trois quarts, le disque se lisait comme une boule) : vu de dessus, le DEVANT EST
    # CARRÉ (un large visage plat où les deux yeux tiennent côte à côte) ; les flancs sont plats (un coussin, pas un
    # ballon) et l'arrière s'amincit ; vu de côté, le contour reste le disque rond
    def galet(v):
        s = np.zeros_like(v)
        rh = np.hypot(v[:, 0], v[:, 1])
        ux = np.where(rh > 1e-9, v[:, 0] / np.maximum(rh, 1e-9), 0.0)
        uy = np.where(rh > 1e-9, v[:, 1] / np.maximum(rh, 1e-9), 0.0)
        p = 1.0 - 0.45 * K.lisse(-uy / 0.6)                       # 1 derrière (rond), 0,55 devant (carré)
        vx = rh * np.sign(ux) * np.abs(ux) ** p
        vy = rh * np.sign(uy) * np.abs(uy) ** p
        vx = np.sign(vx) * np.abs(vx) ** 0.80                      # les flancs plus plats
        epais = 0.235 - 0.080 * K.lisse((vy + 0.1) / 1.1)          # un GALET épais : 0,235 devant, 0,155 derrière (plus une soucoupe sur la tranche)
        s[:, 0] = vx * epais * (1 - 0.30 * np.abs(v[:, 2]) ** 2)
        s[:, 1] = 0.290 * vy                                          # un disque plus HAUT que long
        s[:, 2] = 0.390 * v[:, 2] * (1 - 0.10 * np.clip(-vy, 0, None) ** 1.5 * (v[:, 2] > 0))             # le front qui fuit
        return s
    corps = A.boule(1.0, 64, 32)
    u = corps.v / np.maximum(np.linalg.norm(corps.v, axis=1, keepdims=True), 1e-9)
    t = np.tile(ARGENT, (len(u), 1))
    t[u[:, 2] < -0.35] = NACRE
    rng = np.random.default_rng(8)
    graines = rng.normal(size=(60, 3))
    graines /= np.linalg.norm(graines, axis=1, keepdims=True)
    proche = u @ graines.T > np.cos(0.13 * rng.uniform(0.7, 1.3, 60))[None, :]
    t[proche.any(axis=1)] = GRIS * 0.55 + ARGENT * 0.45
    corps.teinte = t
    a.piece("corps", corps.sculpte(galet), None, pos=(0.0, 0.0, ZC))

    # ----- le clavus : la queue tronquée, un demi-ovale plat qui borde tout l'arrière du disque, au bord en festons -----
    # (18/10) : des festons francs (sept lobes ronds, des creux de 4 cm entre eux) : à 10 %, le gonflage les effaçait
    contour = [(-0.050, 0.300)]
    for th in np.linspace(math.pi / 2, -math.pi / 2, 141):
        phi = (math.pi / 2 - th) / math.pi                          # 0 en haut, 1 en bas
        lobe = abs(math.sin(7 * math.pi * phi))                     # 7 lobes, un creux entre chacun
        nx, nz = math.cos(th) / 0.120, math.sin(th) / 0.290        # la normale de l'ovale de base
        nn = math.hypot(nx, nz)
        k = 0.044 * lobe ** 0.6
        contour.append((0.120 * math.cos(th) + k * nx / nn, 0.290 * math.sin(th) + k * nz / nn))
    contour.append((-0.050, -0.300))
    clavus = A.decoupe(contour, 0.070, 0.025)
    clavus.teinte = np.tile(GRIS, (len(clavus.v), 1))
    a.piece("clavus", couche(clavus, A.cadre((0.0, 0.285, ZC), (1.0, 0.0, 0.0), (0, 0, 1))), None, poil=False)

    # ----- les deux grandes nageoires : épaisses, larges à la base, rejetées vers l'arrière, à l'arrière du disque -----
    aileron = [(-0.130, 0.0), (-0.090, 0.140), (-0.025, 0.280), (0.055, 0.385), (0.115, 0.425), (0.158, 0.400), (0.172, 0.300),
               (0.162, 0.160), (0.140, 0.0)]
    aileron = [(1.20 * x_ + 0.02, 1.30 * y_) for x_, y_ in aileron]               # deux nageoires en AILERON : larges à la base, hautes
    haut = A.decoupe(aileron, 0.074, 0.030)
    haut.teinte = np.tile(GRIS * 1.08, (len(haut.v), 1))
    a.piece("dorsale", couche(haut, A.cadre((0.0, 0.130, ZC + 0.320), (1.0, 0.0, 0.0), (0, 0, 1))), None, poil=False)
    bas = A.decoupe([(x, -y) for x, y in aileron], 0.074, 0.030)
    bas.teinte = np.tile(GRIS * 1.08, (len(bas.v), 1))
    a.piece("anale", couche(bas, A.cadre((0.0, 0.130, ZC - 0.320), (1.0, 0.0, 0.0), (0, 0, 1))), None, poil=False)

    # ----- le visage : deux yeux ronds ouverts, la petite bouche en « o » devant -----
    CENTRE = Vector((0.0, 0.0, ZC))
    for nom, c in (("G", 1), ("D", -1)):
        # (18/10) : sur le visage plat du devant, côte à côte, chacun sur une petite orbite bombée (comme la vraie môle,
        # l'œil un peu saillant) : de trois quarts, l'œil du fond dépasse encore du visage au lieu d'y plonger
        # (« orbite » et non « joue » : la vue de près de la fiche vise les pièces « joue… » et ne cadrait plus que les yeux)
        pos, n = a.surface("corps", CENTRE, Vector((c * 0.22, -0.95, 0.24)))      # DANS la face, à égale distance du bord et de l'axe, à la même hauteur
        n_orb = (n + 1.2 * Vector((c * 0.06, -1.0, 0.08)).normalized()).normalized()   # à peine ouvertes : l'œil du fond se voit de trois quarts
        cj = pos - n * 0.008
        orbite = A.boule(1.0, 28, 14).etire(0.044, 0.044, 0.034)
        orbite.teinte = np.tile(ARGENT, (len(orbite.v), 1))
        a.piece("orbite_" + nom, orbite, None, mat=A.cadre(cj, n_orb, (0, 0, 1)))
        pe, ne = a.surface("orbite_" + nom, cj, n_orb)
        a.oeil("oeil_" + nom, pe + ne * 0.004, ne, 0.0330)      # rond et noir, sans paupière : l'anneau argent faisait un hublot
    p, n = a.surface("corps", CENTRE, Vector((0.0, -0.98, -0.12)))
    lèvre = A.tore(0.022, 0.010, 32, 8)
    a.piece("bouche", lèvre, tuple(GRIS * 0.62), mat=A.cadre(p + n * 0.004, n), poil=False)
    a.tete = CENTRE + Vector((0.0, -0.10, 0.03))                # le gros plan vise le visage entier, pas le flanc

    # ----- deux petites pectorales, qui battent comme des mains ; la gauche pendante -----
    for nom, c in (("G", 1), ("D", -1)):
        pec = A.boule(1.0, 24, 12).etire(0.014, 0.078, 0.086)
        pec.teinte = np.tile(GRIS * 1.1, (len(pec.v), 1))
        a.piece("pectorale_" + nom, pec, None, pos=(c * 0.152, 0.010, ZC - 0.030), rot=(0, 0, c * -22), poil=False)   # sur le flanc (plus épais depuis le 18/10)
    # la fente des ouïes : un trait brodé derrière l'œil, de chaque côté
    for c in (1, -1):
        pts = []
        for u_ in np.linspace(0.0, 1.0, 6):
            q = a.trace("corps", CENTRE, [Vector((c * 0.95, -0.10 + 0.06 * u_, 0.34 - 0.62 * u_))], 0.002)
            if q:
                pts.append(q[0])
        if len(pts) > 1:
            a.broderie("ouie_" + ("G" if c > 0 else "D"), A.courbe(pts, 3), 0.0030, FIL)
    if TOURNE:
        O.tourner(a, TOURNE)
    th = math.radians(TOURNE)
    a.cap_tete = Vector((math.sin(th), -math.cos(th), 0.0))    # l'avant de la tête (tourné avec la bête) : la vue de près
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "poisson")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("poisson_lune", styles.style_de("poisson_lune"), sys.modules[__name__]), "Poisson-lune")
