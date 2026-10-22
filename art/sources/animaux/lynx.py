"""Le lynx en peluche de velours ras, 4e dessin (19/10, refait d'après son modèle 3D : l'auteur avait refusé le 3e, fait à
la main, « hideux » ; l'ancien est gardé dans le scratchpad de l'Artiste). Méthode : vues et mesures de la référence
(references_3d/lynx, CC-BY, regardée seulement : rien n'en est importé ni copié). Ses proportions, relevées sur la
référence (longueur 0,98 m) : le dos plat à 0,52 m, le ventre à 0,25 m (des pattes aussi longues que le corps est
épais), le corps de 0,73 m du poitrail à la croupe, la tête portée devant, à hauteur du dos, la queue de 0,12 m
seulement, tenue à l'horizontale, les pieds larges comme des raquettes.
Cinq traits : debout, haut sur de grosses pattes aux pieds larges ; une tête ronde de chat, le museau court ; des
oreilles pointues terminées par un pinceau noir ; une collerette de favoris pendants, rayés, au bout noir ; une queue
toute courte, au bout noir ; la robe beige grisé semée de petites mouchetures sombres, le dessous crème.

    python lynx.py        fabrique la fiche art/apercus/animaux/lynx.png (velours ras)
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

GONFLAGE = True                                # la base aux volumes de l'Artiste (fusion.py)

ROBE = np.array(M.hexa("#b59a82"))            # la dominante : beige grisé (registre)
CREME = np.array(M.hexa("#efe2cf"))           # le dessous, le museau, le menton, le dedans des oreilles
PIED = np.array(M.hexa("#c4ab92"))            # les pieds, un ton plus clair que la robe
TACHE = np.array(M.hexa("#5a4636"))           # les mouchetures
NOIR = np.array(M.hexa("#2c2420"))            # les pinceaux, le bout des oreilles, de la queue et des favoris
AMBRE = M.hexa("#d4a640")                     # l'iris jaune ambré
TRUFFE = M.hexa("#7a4a44")                    # la truffe brique sombre
PAS = 0.006


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=60, pas=PAS):
    """Une pièce tournée : points = [(fraction de la longueur, rayon), ...] ; les deux bouts se referment en calotte
    arrondie (jamais un tube coupé net)."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def mouchetures(v, cote, rayon, graine=0, proba=0.72):
    """Vrai là où un point tombe dans une tache : des sphères posées au hasard dans un quadrillage en 3D (une par case,
    certaines absentes) ; la surface les coupe en ronds de tailles variées, jamais en carrés (la technique du serval)."""
    v = np.asarray(v, float)
    base = np.floor(v / cote).astype(np.int64)
    dedans = np.zeros(len(v), bool)
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                c = base + np.array([dx, dy, dz], dtype=np.int64)
                h = ((c[:, 0] * 73856093) ^ (c[:, 1] * 19349663) ^ (c[:, 2] * 83492791) ^ (graine * 40503)) & 0x7FFFFFFF

                def alea(m):
                    return ((((h * m) + 12345) >> 9) & 0xFFFF) / 65535.0
                present = alea(1103515245) < proba
                centre = (c + np.stack([alea(214013), alea(1664525), alea(22695477)], axis=1)) * cote
                r = rayon * (0.55 + 0.9 * alea(134775813))
                dedans |= present & (np.linalg.norm(v - centre, axis=1) < r)
    return dedans


def construire():
    a = K.Animal("lynx")
    a.taille = 1.00

    # ----- le corps : un tonneau horizontal, le dos plat, le poitrail profond, le ventre un peu rentré ; moucheté,
    #       le dessous crème -----
    fil = K.Fil([(0.0, 0.410, 0.398), (0.0, 0.200, 0.392), (0.0, 0.000, 0.385), (0.0, -0.200, 0.388), (0.0, -0.330, 0.392)], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.112), (0.12, 0.136), (0.30, 0.136), (0.52, 0.126), (0.74, 0.140), (0.90, 0.145), (1.0, 0.124)], L, 72)
    f = corps.v[:, 2] / L
    corps.v[:, 0] *= 0.86                                                           # plus haut que large
    bas = corps.v[:, 1] < 0
    corps.v[:, 1] *= np.where(bas, 1.0 - 0.10 * np.exp(-((f - 0.48) / 0.18) ** 2) + 0.08 * np.exp(-((f - 0.86) / 0.10) ** 2), 1.0)
    t = np.tile(ROBE, (len(f), 1))
    t[mouchetures(corps.v, 0.042, 0.012, 3, 0.78)] = TACHE
    rho = np.maximum(np.hypot(corps.v[:, 0], corps.v[:, 1]), 1e-9)
    t[corps.v[:, 1] < -0.55 * rho] = CREME                                         # le ventre et le dessous du poitrail
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)

    # ----- le cou : court et épais, la gorge crème -----
    fc = K.Fil([(0.0, -0.240, 0.420), (0.0, -0.330, 0.470), (0.0, -0.410, 0.522)], (1, 0, 0))
    cou = fuseau([(0.0, 0.098), (0.5, 0.090), (1.0, 0.082)], fc.long, 48)
    rc = np.maximum(np.hypot(cou.v[:, 0], cou.v[:, 1]), 1e-9)
    tc = np.tile(ROBE, (len(cou.v), 1))
    tc[mouchetures(cou.v, 0.036, 0.009, 5, 0.6)] = TACHE
    tc[cou.v[:, 1] < -0.35 * rc] = CREME
    cou.teinte = tc
    a.piece("cou", cou.sculpte(fc.couche), None)

    # ----- la tête : ronde et large, une tête de chat, tournée un peu vers nous ; le bas du visage crème -----
    T = A.cadre(Vector((0.0, -0.435, 0.545)), Vector((0.21, -0.978, -0.06)).normalized(), Vector((0, 0, 1)))
    T3 = T.to_3x3()
    cr = A.boule(1.0, 56, 28)
    u = np.array(cr.v, float)

    def crane(v):
        v = K.bosse(K.bosse(v, (0.75, -0.35, 0.45), 0.10, 0.20), (-0.75, -0.35, 0.45), 0.10, 0.20)   # les joues
        v = K.bosse(v, (0.0, 0.55, 0.80), 0.04, 0.25)                                                 # le front
        s = v * [0.112, 0.100, 0.094]
        s[:, 1] *= np.where(s[:, 1] > 0, 0.95, 1.0)                                                    # le crâne un peu plat
        return s
    tt = np.tile(ROBE, (len(u), 1))
    tt[((u[:, 2] > 0.45) & (u[:, 1] < -0.05)) | (u[:, 1] < -0.55)] = CREME                            # le bas du visage, le menton
    cr.teinte = tt
    a.piece("tete", cr.sculpte(crane), None, mat=T)
    a.tete = T @ Vector((0.0, -0.010, 0.050))

    # le museau court : deux coussinets crème, le menton, la truffe brique
    for nom, c in (("G", 1), ("D", -1)):
        a.piece("museau_" + nom, A.boule(1.0, 24, 12).etire(0.030, 0.025, 0.026), tuple(CREME), mat=T @ A.repere((c * 0.021, -0.036, 0.080)))
    a.piece("menton", A.boule(1.0, 24, 12).etire(0.024, 0.016, 0.020), tuple(CREME), mat=T @ A.repere((0.0, -0.064, 0.070)))
    a.piece("truffe", A.boule(1.0, 20, 10).etire(0.017, 0.011, 0.011), TRUFFE, mat=T @ A.repere((0.0, -0.012, 0.100)), poil=False)

    for nom, c in (("G", 1), ("D", -1)):
        # les yeux : de face comme ceux d'un chat, grands ouverts, l'iris ambré autour de la pupille
        regard = T3 @ Vector((c * 0.40, 0.20, 0.89))
        a.rustine("iris_" + nom, "tete", T.to_translation(), regard, 0.22, AMBRE, 0.003, 0)
        p, n = a.surface("tete", T.to_translation(), regard)
        a.oeil("oeil_" + nom, p + n * 0.0035, n, 0.0115)

        # les oreilles : pointues, dressées, le bout noir prolongé par le pinceau ; le dedans crème
        po = A.profil([(0, 0), (0.040, 0.010), (0.040, 0.026), (0.030, 0.052), (0.014, 0.078), (0, 0.090)], 7)
        pb, nb = a.surface("tete", T.to_translation(), T3 @ Vector((c * 0.60, 0.78, -0.14)))
        axe = (Vector(nb).normalized() + (T3 @ Vector((0.0, 0.6, 0.0)))).normalized()      # sur la peau, un peu redressée
        E = A.cadre(Vector(pb) - axe * 0.014, axe, T3 @ Vector((c * 0.20, 0.0, 1.0)))
        o = A.tour(po, 36).etire(1.0, 0.32, 1.0)
        o.teinte = np.where((o.v[:, 2] > 0.060)[:, None], NOIR, ROBE)
        a.piece("oreille_" + nom, o, None, mat=E)
        a.piece("dedans_" + nom, A.tour(po, 28).etire(0.62, 0.30, 0.78).pose((0, 0.009, 0.010)), tuple(CREME), mat=E, poil=False)
        bout = E @ Vector((0.0, 0.0, 0.086))
        pinceau = [bout, bout + axe * 0.026 - T3 @ Vector((c * 0.003, 0.0, 0.0)), bout + axe * 0.052 - T3 @ Vector((c * 0.008, 0.0, 0.0))]
        a.piece("pinceau_" + nom, A.tube(A.courbe([tuple(q) for q in pinceau], 6), lambda t: 0.0065 * (1 - 0.6 * t), 10), tuple(NOIR))

        # la collerette : un favori pendant de chaque côté de la mâchoire, plat, crème rayé de noir, le bout noir
        ff = K.Fil([tuple(T @ Vector((c * 0.080, -0.020, -0.004))), tuple(T @ Vector((c * 0.116, -0.072, -0.016))),
                    tuple(T @ Vector((c * 0.122, -0.132, -0.032)))], tuple(T3 @ Vector((0.0, 0.0, 1.0))))
        fv = fuseau([(0.0, 0.042), (0.30, 0.045), (0.65, 0.030), (0.90, 0.014), (1.0, 0.008)], ff.long, 40, 0.004)
        fv.v[:, 0] *= 0.50                                                         # aplati d'avant en arrière
        fz = fv.v[:, 2] / ff.long
        tf = np.tile(CREME, (len(fz), 1))
        tf[(fz > 0.50) & (fz < 0.62)] = NOIR
        tf[fz > 0.82] = NOIR
        fv.teinte = tf
        a.piece("joue_" + nom, fv.sculpte(ff.couche), None)

    # ----- les pattes avant : droites, épaisses, de grands pieds ronds -----
    for nom, c in (("G", 1), ("D", -1)):
        fa = K.Fil([(c * 0.068, -0.232, 0.400), (c * 0.070, -0.248, 0.250), (c * 0.070, -0.262, 0.110), (c * 0.070, -0.268, 0.040)], (1, 0, 0))
        av = fuseau([(0.0, 0.052), (0.15, 0.052), (0.45, 0.041), (0.75, 0.036), (0.92, 0.036), (1.0, 0.032)], fa.long, 32)
        za = av.v[:, 2] / fa.long
        ta = np.tile(ROBE, (len(za), 1))
        ta[mouchetures(av.v, 0.032, 0.008, 21 + (c > 0), 0.75)] = TACHE
        ta[za > 0.86] = PIED
        av.teinte = ta
        a.piece("patte_av_" + nom, av.sculpte(fa.couche), None)
        a.piece("pied_av_" + nom, A.boule(1.0, 28, 14).etire(0.047, 0.058, 0.030), tuple(PIED), pos=(c * 0.071, -0.282, 0.030), rot=(0, 0, c * 6))

    # ----- les pattes arrière : la cuisse ronde fondue dans la croupe, le genou en avant, le jarret en arrière -----
    for nom, c in (("G", 1), ("D", -1)):
        cu = A.boule(1.0, 36, 18)
        tcu = np.tile(ROBE, (len(cu.v), 1))
        tcu[mouchetures(cu.v * [0.066, 0.120, 0.130], 0.040, 0.012, 11 + (c > 0), 0.78)] = TACHE
        cu.teinte = tcu
        a.piece("cuisse_" + nom, cu.etire(0.066, 0.120, 0.130), None, pos=(c * 0.082, 0.285, 0.345), rot=(-14, 0, 0))
        fr = K.Fil([(c * 0.086, 0.300, 0.380), (c * 0.088, 0.250, 0.265), (c * 0.088, 0.345, 0.140), (c * 0.088, 0.330, 0.040)], (1, 0, 0))
        ar = fuseau([(0.0, 0.054), (0.30, 0.046), (0.55, 0.037), (0.65, 0.035), (0.90, 0.035), (1.0, 0.032)], fr.long, 32)
        zr = ar.v[:, 2] / fr.long
        tr = np.tile(ROBE, (len(zr), 1))
        tr[mouchetures(ar.v, 0.032, 0.008, 31 + (c > 0), 0.75)] = TACHE
        tr[zr > 0.88] = PIED
        ar.teinte = tr
        a.piece("patte_ar_" + nom, ar.sculpte(fr.couche), None)
        a.piece("pied_ar_" + nom, A.boule(1.0, 28, 14).etire(0.045, 0.058, 0.030), tuple(PIED), pos=(c * 0.088, 0.318, 0.030), rot=(0, 0, c * 4))

    # ----- la queue : toute courte, tenue à l'horizontale, le bout noir arrondi -----
    fq = K.Fil([(0.0, 0.380, 0.468), (0.0, 0.445, 0.496), (0.0, 0.505, 0.514)], (1, 0, 0))
    queue = fuseau([(0.0, 0.034), (0.40, 0.035), (0.80, 0.032), (1.0, 0.030)], fq.long, 32, 0.005)
    zq = queue.v[:, 2] / fq.long
    tq = np.tile(ROBE, (len(zq), 1))
    tq[zq > 0.66] = NOIR
    queue.teinte = tq
    a.piece("queue", queue.sculpte(fq.couche), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("lynx", styles.style_de("lynx"), sys.modules[__name__]), "Lynx")
