"""Le casoar en peluche de magasin, 4e dessin (19/10 : refait d'après son modèle 3D, references_3d/casoar, CC-BY, VUES
SEULEMENT : rien n'en est importé ni copié ; l'ancien, fait à la main : casoar_ancien.py, et la version du 18/10 refusée
par l'auteur dans le scratchpad de l'Artiste). Méthode : vues et mesures du modèle de référence (de profil, de face, de
dessus, la tête de près), puis modelage à nous à ses proportions.

Mesures de la référence (hauteur 1,13 ; longueur du bec à la croupe 1,90 ; largeur 0,73 ; la tête vers -Y) :
- le corps : un gros œuf en fuseau vu de dessus (pointu devant vers le cou, rond derrière), de y -0,58 à +0,95, son
  dessous à 0,45 et son dos à 1,08 (95 % de la hauteur), le plus large (0,73) un peu en arrière du milieu ;
- le cou : COURT et épais, qui part en avant et en haut du poitrail, creusé derrière la tête ; la tête à peine plus
  haute que le dos (l'œil à 0,92, le dos à 1,08) ;
- le casque : une haute lame cornée, étroite vue de face (0,04 à 0,09), qui monte de la base du bec jusqu'à 1,13,
  aussi haute que la tête ;
- le bec : 0,15, fort, à peine courbé vers le bas ; l'œil sur le côté, sous le casque ;
- deux caroncules plates et longues (0,25) qui pendent côte à côte sous la gorge, presque jusqu'au bas du corps ;
- les pattes : fortes, 40 % de la hauteur, écartées (pieds à ±0,2), trois doigts vers l'avant.

Cinq traits : un gros corps noir couvert de plumes qui pendent comme des crins ; un casque corné haut sur la tête ; un
cou court, nu, bleu vif, la nuque rouge, et deux caroncules rouges qui pendent ; un bec fort ; de grosses pattes grises à
trois doigts.

    python casoar.py        fabrique la fiche art/apercus/animaux/casoar.png (peluche de magasin, palier 4)
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
import peluche as K

GONFLAGE = False                              # sans gonflage : il fondait les crins en une boule lisse (18/10)


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


ENCRE = np.array(M.hexa("#35405a"))           # la dominante : noir bleuté (le poil la fonce)
CRINS = [np.array(M.hexa(h)) for h in ("#2c3448", "#35405a", "#404b66")]   # les crins : trois noirs, pour le relief
COBALT = np.array(M.hexa("#2f7cf0"))          # le cou et la tête nus : bleu cobalt
CIEL = np.array(M.hexa("#5aa6f4"))            # la face et la gorge : un bleu plus clair
ROUGE = np.array(M.hexa("#f02838"))           # la nuque, les caroncules
PATTE = np.array(M.hexa("#8c8a84"))           # les pattes : gris
IVOIRE = M.hexa("#f4e8c0")                    # le casque
BEC = M.hexa("#3a3a40")                       # le bec : noir
ONGLE = M.hexa("#4a4644")                     # les ongles
OEIL = M.hexa("#8a5228")                      # l'iris brun orangé

# ----- le corps, aux mesures de la référence (la tête vers -Y, le sol à 0) -----
CY, CZ = 0.19, 0.77                           # le centre : un peu en arrière du milieu, le dessous à 0,48
AX, AY, AZ = 0.33, 0.72, 0.29                 # demi-largeur, demi-longueur, demi-hauteur (les crins ajoutent ~2 cm)


def corps_forme(u):
    """Le corps : un point de la boule unité -> un point du corps. Vu de dessus un fuseau, pointu devant (le poitrail
    qui file vers le cou), rond derrière ; les deux bouts un peu tombants (référence : le dos culmine à 1,08 au tiers
    arrière, le poitrail est à 0,72, la croupe à 0,68)."""
    u = np.asarray(u, float)
    t = u[:, 1]
    devant = np.minimum(t, 0.0)
    derriere = np.maximum(t, 0.0)
    fuseau = 1.0 - 0.33 * devant ** 2 - 0.10 * derriere ** 2
    tombe = -0.08 * devant ** 2 - 0.12 * derriere ** 2
    dos = 0.025 * np.maximum(u[:, 2], 0.0) * np.exp(-((t - 0.10) / 0.45) ** 2)       # le dos un peu plus haut au milieu
    return np.stack([AX * u[:, 0] * fuseau, CY + AY * t, CZ + AZ * u[:, 2] * fuseau + tombe + dos], axis=1)


def corps_normale(u):
    """La normale du corps en ces points de la boule unité (par différences finies sur la forme)."""
    u = np.asarray(u, float)
    a = np.where(np.abs(u[:, 2:3]) < 0.9, np.array([[0.0, 0.0, 1.0]]), np.array([[1.0, 0.0, 0.0]]))
    e1 = np.cross(u, a)
    e1 /= np.linalg.norm(e1, axis=1, keepdims=True)
    e2 = np.cross(u, e1)
    h = 1e-3
    p = corps_forme(u)
    d1 = corps_forme((u + h * e1) / np.linalg.norm(u + h * e1, axis=1, keepdims=True)) - p
    d2 = corps_forme((u + h * e2) / np.linalg.norm(u + h * e2, axis=1, keepdims=True)) - p
    n = np.cross(d1, d2)
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    return np.where(np.sum(n * (p - [0.0, CY, CZ]), axis=1, keepdims=True) < 0, -n, n)


def crin(rng, u0):
    """Un crin : il part du corps, se couche sur lui en descendant de part et d'autre de la raie du dos (en tournant
    autour de l'axe du corps, un peu vers la queue, comme les plumes de la référence), et ce qui dépasse sous le ventre
    pend librement, un peu écarté. Rend le tracé (points du monde) ou None."""
    uy = float(u0[1])
    rho = math.sqrt(max(1e-6, 1.0 - uy * uy))
    psi = math.atan2(float(u0[0]), float(u0[2]))                 # 0 sur la raie du dos, +-pi/2 sur les flancs
    sens = 1.0 if (u0[0] > 0 or (abs(u0[0]) < 1e-3 and rng.random() < 0.5)) else -1.0
    longueur = 0.13 + 0.13 * rng.random()
    pts, fait, k = [], 0.0, 0
    u = np.array([[u0[0], u0[1], u0[2]]])
    while fait < longueur and abs(psi) < math.pi - 0.25:
        rho = math.sqrt(max(1e-6, 1.0 - uy * uy))
        u = np.array([[rho * math.sin(psi), uy, rho * math.cos(psi)]])
        if u[0, 2] < -0.30:
            break
        decolle = -0.004 if k == 0 else 0.006 + 0.010 * min(1.0, fait / 0.10)
        p = corps_forme(u)[0] + corps_normale(u)[0] * decolle
        if pts:
            fait += float(np.linalg.norm(p - pts[-1]))
        pts.append(p)
        psi += sens * 0.06 / max(rho, 0.30)
        uy = min(0.97, uy + 0.012)                               # couché un peu vers la queue
        k += 1
    reste = longueur - fait
    if reste > 0.02 and pts:                                     # sous le ventre : il pend, à peine écarté
        n = corps_normale(u)[0]
        dehors = np.array([n[0], n[1], 0.0])
        dehors = dehors / max(1e-6, float(np.linalg.norm(dehors))) * 0.22
        bas = pts[-1]
        for f in (0.35, 0.70, 1.0):
            pts.append(bas + (dehors * f * f + np.array([0.0, 0.0, -1.0])) * reste * f)
    pts = propres([tuple(p) for p in pts], 4e-3)
    return pts if len(pts) >= 3 else None


def fuseau_tourne(points, longueur, cotes=36, pas=0.006):
    """Une pièce tournée très finement échantillonnée (fraction, rayon), couchée ensuite le long d'un fil ; les deux bouts
    se referment en calotte arrondie (le cou du flamant rose gardé par l'auteur)."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    k = np.ones(7) / 7
    rayons = np.convolve(np.pad(np.interp(s / longueur, f, r), 3, mode="edge"), k, "valid")
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("casoar")
    a.taille = 1.70

    # ----- le corps : le gros œuf en fuseau de la référence, en peluche noire -----
    corps = A.boule(1.0, 64, 32)
    corps.sculpte(corps_forme)
    corps.teinte = np.tile(ENCRE, (len(corps.v), 1))
    a.piece("corps", corps, None)

    # ----- les crins : couchés sur le dos et les flancs, ils retombent et pendent en frange sous le ventre et la croupe -----
    rng = np.random.default_rng(19)
    plumage, n = None, 0
    while n < 360:
        u0 = rng.normal(size=3)
        u0 /= np.linalg.norm(u0)
        if u0[2] < -0.30 or u0[1] < -0.86:                       # ni sous le ventre, ni au bout du poitrail (le cou y entre)
            continue
        trace = crin(rng, u0)
        if trace is None:
            continue
        r0 = 0.017 + 0.007 * rng.random()
        m = A.tube(A.courbe(trace, 3), lambda t, r0=r0: r0 * (1.0 - 0.80 * t), 7)
        m.teinte = np.tile(CRINS[int(rng.integers(0, 3))], (len(m.v), 1))
        plumage = m if plumage is None else plumage + m
        n += 1
    a.piece("plumage", plumage, None)

    # ----- le cou : court et épais, il part en avant et en haut du poitrail ; nu, bleu cobalt, la nuque rouge, le pied
    #       noir sous les crins -----
    enc = K.Fil([(0.0, -0.34, 0.70), (0.0, -0.46, 0.725), (0.0, -0.555, 0.785), (0.0, -0.625, 0.850), (0.0, -0.670, 0.895)], (1, 0, 0))
    Lc = enc.long
    cou = fuseau_tourne([(0.0, 0.130), (0.22, 0.106), (0.50, 0.092), (0.80, 0.086), (1.0, 0.084)], Lc, 40)
    fr = np.clip(cou.v[:, 2] / Lc, 0.0, 1.0)
    angle = np.arctan2(cou.v[:, 1], cou.v[:, 0])                  # +Y de la pièce = la nuque (le dessus du fil)
    teinte = np.tile(COBALT, (len(cou.v), 1))
    teinte[(fr > 0.16) & (fr < 0.58) & (np.abs(angle - math.pi / 2) < 1.15)] = ROUGE          # la nuque rouge
    teinte[(fr > 0.45) & (np.abs(angle + math.pi / 2) < 0.9)] = CIEL                            # la gorge plus claire
    teinte[fr <= 0.18] = ENCRE                                                                     # le pied du cou, sous les crins
    cou.teinte = teinte
    a.piece("cou", cou.sculpte(enc.couche), None)            # en peluche : lisse, un cou fait tube (18/10)

    # ----- la tête : un peu grosse (peluche), pointée 15° vers le bas comme sur la référence -----
    H = A.cadre(Vector((0.0, -0.690, 0.905)), Vector((0.0, -1.0, -0.25)).normalized(), Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = A.boule(1.0, 40, 20).etire(0.105, 0.112, 0.128)
    tete.teinte = np.tile(COBALT, (len(tete.v), 1))
    tete.teinte[tete.v[:, 2] > 0.062] = CIEL                      # la face, autour du bec
    a.piece("tete", tete, None, mat=H, poil=False)
    a.tete = H @ Vector((0.0, 0.022, 0.112))

    # le bec : fort, à peine courbé vers le bas, sa base dans la tête
    def courbe_bec(v):
        v = v * [0.80, 1.0, 1.08]
        v[:, 1] -= 1.5 * np.maximum(v[:, 2] - 0.065, 0.0) ** 2
        return v
    bec = A.tour(A.profil([(0, 0), (0.048, 0.006), (0.050, 0.030), (0.044, 0.070), (0.032, 0.112), (0.018, 0.148), (0.007, 0.166), (0, 0.172)], 6), 32)
    a.piece("bec", bec.sculpte(courbe_bec), BEC, mat=H @ A.repere((0.0, -0.016, 0.075)), poil=False)

    # le casque : un heaume corné arrondi (pas une corne) : long à sa base comme la tête, étroit vu de face, il monte de
    # la base du bec, le sommet rond au-dessus de l'œil, l'arrière plus droit (profil de la référence)
    def lame(v):
        h = (v[:, 1] + 1.0) / 2.0
        return np.stack([0.042 * (1.0 - 0.35 * h) * v[:, 0],
                         0.125 * v[:, 1],
                         0.090 * (1.0 - 0.30 * h) * v[:, 2] - 0.050 * h], axis=1)
    a.piece("casque", A.boule(1.0, 48, 24).sculpte(lame), IVOIRE, mat=H @ A.repere((0.0, 0.088, 0.048)), poil=False)

    # les yeux : de chaque côté sous le casque, tournés assez vers l'avant pour se voir tous les deux de face
    for nom, c in (("G", 1), ("D", -1)):
        regard = H3 @ Vector((c * 0.66, 0.24, 0.70))
        a.rustine("iris_" + nom, "tete", H.to_translation(), regard, 0.30, OEIL, 0.003, 0)
        p, nrm = a.surface("tete", H.to_translation(), regard)
        a.oeil("oeil_" + nom, p + nrm * 0.004, nrm, 0.0250)

    # les deux caroncules : plates, longues, côte à côte sous la gorge, le haut cousu dans le cou
    s = 0.62 * Lc
    centre, avant, nuque = enc.cadre(s)
    for nom, c in (("G", 1), ("D", -1)):
        depart = Vector(centre) + Vector((c * 0.030, 0.0, 0.0))
        p, _nrm = a.surface("cou", depart, -Vector(nuque))
        haut = p + Vector(nuque) * 0.018
        car = A.tour(A.profil([(0, 0), (0.016, 0.010), (0.020, 0.050), (0.030, 0.130), (0.036, 0.180), (0.030, 0.212), (0.015, 0.228), (0, 0.232)], 6), 24)
        car.etire(1.0, 0.40, 1.0)                                 # plate : large de face, mince de profil
        a.piece("caroncule_" + nom, car, tuple(ROUGE), mat=A.repere(tuple(haut), (180, c * -7, 0)), poil=False)

    # ----- les pattes : fortes, écartées, la cuisse sous les crins ; trois gros doigts vers l'avant -----
    for nom, c in (("G", 1), ("D", -1)):
        ch = [(c * 0.118, 0.140, 0.580), (c * 0.128, 0.160, 0.380), (c * 0.138, 0.175, 0.210), (c * 0.148, 0.120, 0.055)]
        m = A.tube(A.courbe(propres(ch), 8), lambda t: 0.043 + 0.030 * (1.0 - t) ** 2, 18)
        m.teinte = np.tile(PATTE, (len(m.v), 1))
        a.piece("jambe_" + nom, m, None, poil=False)
        talon = np.array([c * 0.150, 0.112, 0.040])
        a.piece("pied_" + nom, A.boule(1.0, 24, 12).etire(0.050, 0.058, 0.036), tuple(PATTE), pos=tuple(talon), poil=False)
        for k, (angle_, long_, r_) in enumerate(((c * 30.0, 0.120, 0.024), (c * 6.0, 0.165, 0.028), (-c * 24.0, 0.130, 0.026))):
            th = math.radians(angle_)
            d = np.array([math.sin(th), -math.cos(th), 0.0])
            bout = talon + d * long_
            trace = [tuple(talon), tuple(talon + d * long_ * 0.5 + [0.0, 0.0, 0.010]), tuple(bout + [0.0, 0.0, -0.016])]
            doigt = A.tube(A.courbe(propres(trace), 6), lambda t, r_=r_: r_ * (1.0 - 0.30 * t), 14)
            doigt.teinte = np.tile(PATTE, (len(doigt.v), 1))
            a.piece("orteil_%s_%d" % (nom, k), doigt, None, poil=False)
            griffe = A.tour(A.profil([(0, 0), (0.014, 0.004), (0.013, 0.016), (0.008, 0.030), (0.003, 0.038), (0, 0.040)], 5), 16)
            g = 1.35 if k == 2 else 1.0                          # le doigt intérieur porte la grande griffe
            a.piece("griffe_%s_%d" % (nom, k), griffe.etire(1.0, 0.85, g), ONGLE,
                    mat=A.cadre(Vector(tuple(bout + [0.0, 0.0, -0.016] - d * 0.012)), Vector(tuple(d + [0.0, 0.0, -0.35]))), poil=False)
    return a


# ---------------------------------------------------------------- pour le jeu : squelette et animations (rig_auto.py)
# (19/10 : la fiche gardée par l'auteur n'avait plus de squelette ; usine.py échouait sur PORTEURS. La forme ne change pas.)
from rig_auto import rig
if __name__ != "__main__":
    OS, PORTEURS, ANIMATIONS = rig(sys.modules.get(__name__) or construire, "oiseau")


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("casoar", styles.style_de("casoar"), sys.modules[__name__]), "Casoar")
