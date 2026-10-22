"""Le guépard en peluche (6e dessin, 19/10/2026 : refait D'APRÈS SON MODÈLE 3D. La référence, references_3d/guepard
(CC-BY, Pigcraft), n'a servi qu'à des VUES et à des MESURES ; rien n'en est importé ni copié : chaque volume est modelé
ici. l'auteur avait refusé le 5e dessin, fait à la main d'après le dingo).

Debout sur ses quatre longues pattes, comme le modèle : un corps long et fin, le thorax profond, la taille très
creusée qui remonte vers l'aine, la croupe à peine plus haute que le garrot ; une PETITE tête ronde portée haut sur un
cou épais, un museau court, de petites oreilles rondes au dos noir, les deux LARMES noires du coin de l'œil au coin de
la bouche, le menton et la poitrine crème ; des taches noires PLEINES et rondes semées serrées sur un fond doré ; une
longue queue qui tombe droit puis se relève, tachée à la racine, ANNELÉE de noir au bout, le bout blanc.
La tête un peu tournée vers nous, l'œil d'ambre.

Les mesures du modèle (19/10, scratchpad guepard/ : six vues orthographiques et des tranches) : longueur 0,98 du museau
au bout de la queue, hauteur 0,584 aux oreilles ; garrot 0,51, croupe 0,50, creux du dos 0,47 ; poitrine profonde
(dessous à 0,24), la taille remontée (dessous à 0,30-0,32) et fine (demi-largeur 0,054 contre 0,09 au thorax) ; la
tête : 0,14 de long, 0,125 de haut, l'œil au tiers avant ; pattes avant droites sous la poitrine (x 0,064), pattes
arrière plus écartées (x 0,09-0,11), le genou en avant, le jarret haut (0,15-0,18). Ici tout est à l'échelle 1,5 du
modèle, la tête à 1,8 (une tête de peluche un peu plus grosse, mais toujours petite devant le corps).

Les 5 traits de l'espèce : 1. un félin mince sur de longues pattes, le corps long, la taille creusée ; 2. une petite
tête ronde, de petites oreilles rondes ; 3. les deux larmes noires de l'œil à la bouche ; 4. le pelage doré semé de
taches noires pleines et rondes, le dessous crème ; 5. une longue queue annelée de noir au bout, le bout blanc.

    python guepard.py        fabrique la fiche art/apercus/animaux/guepard.png, sa copie reel/guepard_apres.png et la tête
                             de près reel/guepard_tete.png
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

GONFLAGE = True       # la base aux volumes gonflés de l'Artiste (fusion.py) : jointures fondues, bouts arrondis

# le style B (palier 4) ramène les couleurs vers leur gris : la dominante est donnée très dorée pour rester dorée
OR = np.array(M.hexa("#ffb41c"))              # la dominante : or doré
CREME = np.array(M.hexa("#fff4e2"))           # le ventre, la poitrine, la gorge, le menton, le bout de la queue
NOIR = np.array(M.hexa("#1c1715"))            # les taches, les larmes, les anneaux, le dos des oreilles
AMBRE = M.hexa("#f2a01e")                     # l'iris
TRUFFE = M.hexa("#2b2321")
PAS = 0.006

TETE = Vector((0.0, -0.655, 0.765))           # le centre de la tête (modèle : 0 ; -0,425 ; 0,505, fois 1,5)
LACET = 15.0                                  # la tête tournée vers nous (+X), comme sur le modèle


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=56, pas=PAS):
    """Une pièce tournée le long de Z, de rayon donné par (fraction, rayon) ; les deux bouts fermés en calotte ronde."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def taches(v, permis, ecart, rayon, graine):
    """Des taches noires PLEINES et rondes, semées régulièrement SUR la surface : des centres pris parmi les points permis,
    écartés d'au moins « ecart » les uns des autres, chacun un disque de « rayon » (plus ou moins 25 %). Rend un booléen
    par point. (Le 5e dessin semait des boules dans un quadrillage 3D : peu d'entre elles touchaient la peau, d'où des
    taches rares et rognées.)"""
    v = np.asarray(v, float)
    rng = np.random.default_rng(graine)
    ordre = np.nonzero(permis)[0]
    rng.shuffle(ordre)
    grille, centres = {}, []
    for i in ordre:
        p = v[i]
        c = tuple(np.floor(p / ecart).astype(int))
        libre = True
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    for q in grille.get((c[0] + dx, c[1] + dy, c[2] + dz), ()):
                        if float(np.sum((q - p) ** 2)) < ecart * ecart:
                            libre = False
                            break
                    if not libre:
                        break
                if not libre:
                    break
        if libre:
            grille.setdefault(c, []).append(p)
            centres.append(p)
    dedans = np.zeros(len(v), bool)
    for p in centres:
        r = rayon * rng.uniform(0.75, 1.25)
        dedans |= np.sum((v - p) ** 2, axis=1) < r * r
    return dedans & permis


def surface_vers(m, d):
    """Le point de la maille (une tête tournée autour de son centre, à l'origine) dans la direction d."""
    u = m.v / np.maximum(np.linalg.norm(m.v, axis=1, keepdims=True), 1e-9)
    d = np.asarray(d, float) / np.linalg.norm(d)
    return m.v[int(np.argmax(u @ d))]


def trait(m, directions, demi_large, n=60):
    """Les points de la maille à moins de demi_large d'un trait tracé sur la surface par des directions (depuis le centre)."""
    dirs = [np.asarray(d, float) / np.linalg.norm(d) for d in directions]
    chemin = A.courbe(dirs, 12)
    pts = np.array([surface_vers(m, d) for d in chemin])
    pts = np.array([pts[0]] + [p for a_, b_ in zip(pts[:-1], pts[1:]) for p in np.linspace(a_, b_, 6)[1:]])
    dedans = np.zeros(len(m.v), bool)
    for p in pts:
        dedans |= np.sum((m.v - p) ** 2, axis=1) < demi_large * demi_large
    return dedans


def construire():
    a = K.Animal("guepard")
    a.taille = 1.50
    a.poil_long = 0.0030                       # un poil ras (le style B le rallonge) : les taches, les larmes se lisent
    a.gonflage_reglages = {"pression": 0.12, "fins": 0.0}    # un coureur mince : ni ventre ballon, ni pattes en boudins

    # ----- le corps : de la croupe (Y +0,42) au poitrail (Y -0,54), le long de la ligne du dos du modèle ; section en
    # ovale debout (plus haut que large), le thorax profond, la taille creusée et fine -----
    fil = K.Fil([(0.0, y, z) for y, z in ((0.420, 0.612), (0.200, 0.603), (0.000, 0.592), (-0.200, 0.553), (-0.400, 0.562),
                                          (-0.540, 0.590))], (1, 0, 0))
    L = fil.long
    hauts = [(0.000, 0.072), (0.063, 0.088), (0.140, 0.120), (0.234, 0.140), (0.328, 0.146), (0.420, 0.150), (0.516, 0.164),
             (0.610, 0.172), (0.703, 0.184), (0.797, 0.204), (0.890, 0.200), (1.000, 0.180)]
    corps = fuseau(hauts, L, 180)
    f = corps.v[:, 2] / L
    larges = np.interp(f, [0.0, 0.14, 0.26, 0.34, 0.42, 0.52, 0.64, 0.72, 0.82, 0.92, 1.0],
                       [0.95, 0.90, 0.82, 0.74, 0.64, 0.66, 0.80, 0.78, 0.71, 0.70, 0.72])
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))          # 0 sur le dos, pi sous le ventre (avant la mise en ovale)
    corps.v[:, 0] *= larges
    corps.sculpte(fil.couche)
    ventre = th > np.interp(f, [0.0, 0.70, 0.86, 1.0], [2.30, 2.25, 2.02, 1.88])
    t = np.tile(OR, (len(f), 1))
    t[ventre] = CREME
    t[taches(corps.v, ~ventre & (th < np.interp(f, [0.0, 0.70, 0.86, 1.0], [2.15, 2.10, 1.88, 1.74])), 0.050, 0.0150, 1)] = NOIR
    corps.teinte = t
    a.piece("corps", corps, None)

    # ----- la tête : petite et ronde, le museau court, le menton crème ; tournée vers nous -----
    T = A.repere(TETE, (0, 0, LACET))
    T3 = T.to_3x3()

    def tete_f(v):
        v = K.bosse(v, (0.0, -0.93, -0.40), 0.32, 0.15)            # le museau, court mais net (l'œil à 5 cm de la truffe)
        for c in (1, -1):
            v = K.bosse(v, (c * 0.55, -0.78, -0.45), 0.10, 0.10)   # les coussinets des moustaches
            v = K.bosse(v, (c * 1.00, -0.10, -0.30), 0.07, 0.30)   # les joues
        v = K.bosse(v, (0.0, -0.55, -0.85), 0.08, 0.12)            # le menton
        return v * [0.104, 0.100, 0.097]
    tete = A.boule(1.0, 160, 80).sculpte(tete_f)
    u = tete.v / np.linalg.norm(tete.v, axis=1, keepdims=True)
    tt = np.tile(OR, (len(u), 1))
    creme = ((u[:, 2] < -0.28) & (np.abs(u[:, 0]) > 0.10) & (u[:, 1] < -0.35)) | (u[:, 2] < -0.55) | ((u[:, 2] < -0.36) & (u[:, 1] < -0.72))
    tt[creme] = CREME
    oeil_g = np.array([0.48, -0.82, 0.30]) / np.linalg.norm([0.48, -0.82, 0.30])
    loin_des_yeux = np.minimum(np.linalg.norm(u - oeil_g * [1, 1, 1], axis=1), np.linalg.norm(u - oeil_g * [-1, 1, 1], axis=1)) > 0.42
    haut_tete = ((u[:, 2] > 0.42) | (u[:, 1] > 0.25)) & ~creme & loin_des_yeux
    tt[taches(tete.v, haut_tete, 0.022, 0.0068, 7)] = NOIR           # les petits points du front et de la nuque
    for c in (1, -1):                                                # les LARMES : du coin de l'œil au coin de la bouche
        e = oeil_g * [c, 1, 1]
        coin = e + 0.27 * np.array([-c * 0.55, -0.05, -0.83])
        tt[trait(tete, [coin, (c * 0.27, -0.93, 0.03), (c * 0.25, -0.92, -0.19), (c * 0.27, -0.84, -0.42),
                        (c * 0.30, -0.77, -0.56)], 0.0078)] = NOIR
        tt[trait(tete, [(0.0, -0.86, -0.50), (c * 0.10, -0.86, -0.56), (c * 0.24, -0.79, -0.58)], 0.0034)] = NOIR   # la bouche
    tt[trait(tete, [(0.0, -0.90, -0.40), (0.0, -0.86, -0.50)], 0.0034)] = NOIR
    tete.teinte = tt
    a.piece("tete", tete, None, mat=T)
    nez = surface_vers(tete, (0.0, -0.94, -0.33))
    a.piece("truffe", A.boule(1.0, 24, 12).sculpte(lambda v: K.bosse(v, (0, 0, 1), 0.25, 0.4)).etire(0.017, 0.012, 0.012), TRUFFE,
            mat=T @ A.repere(tuple(nez + np.array([0.0, 0.004, 0.003])), (-18, 0, 0)), poil=False)
    a.tete = T @ Vector((0.0, -0.100, 0.000))

    # ----- les yeux : deux yeux de feutrine ronds, grands ouverts, l'iris d'ambre ; posés DANS la tête tournée -----
    for nom, c in (("G", 1), ("D", -1)):
        a.rustine("iris_" + nom, "tete", T.to_translation(), T3 @ Vector((c * 0.48, -0.82, 0.30)), 0.25, AMBRE, 0.003, 0)
    for nom, c in (("G", 1), ("D", -1)):                         # symétriques DANS la tête tournée (paire_yeux, R=)
        p_, n_ = a.surface("tete", T.to_translation(), T3 @ Vector((c * 0.48, -0.82, 0.30)))
        a.oeil("oeil_" + nom, p_ + n_ * 0.004, n_, 0.0175)

    # ----- les oreilles : petites, rondes, basses et écartées aux coins du crâne (pas des oreilles d'ourson) ; le dos noir,
    # le dedans crème -----
    po = A.profil([(0, 0), (0.032, 0.004), (0.038, 0.018), (0.034, 0.034), (0.021, 0.046), (0, 0.050)], 6)
    for nom, c in (("G", 1), ("D", -1)):
        base = Vector(surface_vers(tete, (c * 0.66, 0.34, 0.67)))
        vers = (T3 @ Vector((c * 0.58, 0.18, 0.80))).normalized()
        E = A.cadre(T @ base - vers * 0.008, vers, T3 @ Vector((c * 0.25, -1.0, 0.0)))
        oreille = A.tour(po, 40).etire(1.0, 0.38, 1.0)
        ot = np.tile(OR, (len(oreille.v), 1))
        ot[(oreille.v[:, 1] < 0.0) & (np.hypot(oreille.v[:, 0], oreille.v[:, 2] - 0.019) < 0.026)] = NOIR    # le dos noir
        oreille.teinte = ot
        a.piece("oreille_" + nom, oreille, None, mat=E)
        a.piece("interieur_" + nom, A.tour(po, 28).etire(0.55, 0.30, 0.70).pose((0, 0.005, 0.007)), tuple(CREME), mat=E, poil=False)

    # ----- le cou : épais, de la poitrine à l'arrière de la tête, la gorge crème -----
    cf = K.Fil([(0.0, -0.420, 0.580), (0.0, -0.530, 0.680), tuple(T @ Vector((0.0, 0.040, -0.030)))], (1, 0, 0))
    cou = fuseau([(0.0, 0.112), (0.5, 0.100), (1.0, 0.084)], cf.long, 96)
    thc = np.abs(np.arctan2(cou.v[:, 0], cou.v[:, 1]))
    cou.sculpte(cf.couche)
    ct = np.tile(OR, (len(thc), 1))
    ct[thc > 1.95] = CREME
    ct[taches(cou.v, thc < 1.75, 0.040, 0.0115, 11)] = NOIR
    cou.teinte = ct
    a.piece("cou", cou, None)

    # ----- les pattes : longues et fines ; devant, droites sous la poitrine ; derrière, la cuisse large, le genou en
    # avant, le jarret haut ; des pieds ronds -----
    def jambe(pts, rayons, graine, haut_taches=0.62):
        ft = K.Fil(pts, (1, 0, 0))
        m = fuseau([(i / (len(rayons) - 1), r) for i, r in enumerate(rayons)], ft.long, 48, 0.005)
        m.sculpte(ft.couche)
        mt = np.tile(OR, (len(m.v), 1))
        mt[taches(m.v, (m.v[:, 2] > 0.075) & (m.v[:, 2] < haut_taches), 0.036, 0.0110, graine)] = NOIR
        m.teinte = mt
        return m

    for nom, c in (("G", 1), ("D", -1)):
        av = [(c * 0.088, -0.420, 0.650), (c * 0.100, -0.355, 0.400), (c * 0.097, -0.395, 0.200), (c * 0.097, -0.405, 0.095),
              (c * 0.099, -0.415, 0.050)]
        a.piece("patte_av_" + nom, jambe(av, [0.074, 0.060, 0.050, 0.045, 0.042, 0.040, 0.039, 0.038], 20 + c), None)
        pied = A.boule(1.0, 32, 16).sculpte(lambda v: K.bosse(v, (0, -1, 0.2), 0.10, 0.30)).etire(0.041, 0.056, 0.034)
        a.piece("pied_av_" + nom, pied.peint(tuple(OR)), None, pos=(c * 0.100, -0.434, 0.034))

        cuisse = A.boule(1.0, 64, 32).etire(0.052, 0.118, 0.160)
        cu = np.tile(OR, (len(cuisse.v), 1))
        cuisse.pose((c * 0.088, 0.215, 0.500), (-22, 0, 0))
        cu[taches(cuisse.v, cuisse.v[:, 0] * c > 0.06, 0.042, 0.0130, 30 + c)] = NOIR
        cuisse.teinte = cu
        a.piece("cuisse_" + nom, cuisse, None)
        ar = [(c * 0.100, 0.240, 0.580), (c * 0.122, 0.135, 0.385), (c * 0.130, 0.250, 0.290), (c * 0.135, 0.385, 0.215),
              (c * 0.142, 0.345, 0.110), (c * 0.146, 0.322, 0.052)]
        a.piece("patte_ar_" + nom, jambe(ar, [0.066, 0.056, 0.046, 0.041, 0.040, 0.039, 0.037, 0.036, 0.036], 40 + c, 0.52), None)
        pied = A.boule(1.0, 32, 16).sculpte(lambda v: K.bosse(v, (0, -1, 0.2), 0.10, 0.30)).etire(0.041, 0.058, 0.034)
        a.piece("pied_ar_" + nom, pied.peint(tuple(OR)), None, pos=(c * 0.147, 0.298, 0.034))

    # ----- la queue : longue, elle tombe droit puis se relève en crochet ; tachée à la racine, annelée de noir au bout,
    # le bout blanc -----
    qf = K.Fil([(0.0, 0.330, 0.670), (0.0, 0.410, 0.640), (0.004, 0.455, 0.520), (0.008, 0.478, 0.400), (0.018, 0.505, 0.310),
                (0.035, 0.555, 0.258), (0.058, 0.625, 0.248), (0.080, 0.682, 0.282), (0.095, 0.718, 0.335)], (1, 0, 0))
    queue = fuseau([(0.0, 0.044), (0.15, 0.040), (0.50, 0.034), (0.80, 0.032), (0.92, 0.035), (1.0, 0.036)], qf.long, 48, 0.005)
    fq = queue.v[:, 2] / qf.long
    queue.sculpte(qf.couche)
    qt = np.tile(OR, (len(fq), 1))
    qt[taches(queue.v, (fq > 0.08) & (fq < 0.50), 0.040, 0.0115, 50)] = NOIR
    anneaux = (fq >= 0.54) & (fq < 0.92) & (((fq - 0.54) / 0.076) % 1.0 < 0.48)
    qt[anneaux] = NOIR
    qt[fq >= 0.92] = CREME
    queue.teinte = qt
    a.piece("queue", queue, None)
    return a


def gros_plan(a):
    """La tête de près, de face et de trois quarts (art/apercus/reel/guepard_tete.png, comme essais/reel/bete.gros_plan),
    et la fiche copiée en art/apercus/reel/guepard_apres.png : la planche avant / après sans passer par la référence
    (son fichier de 118 Mo ne passe que sur Kaggle). La bête est encore dans la scène après sa fiche."""
    import shutil
    from PIL import Image
    apercus = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "apercus"))
    sortie = os.path.join(apercus, "reel")
    os.makedirs(sortie, exist_ok=True)
    bas, haut = a.boite()
    L = float(max(haut - bas))
    tete = Vector(a.tete)
    img = Image.new("RGB", (1920, 720), (20, 20, 20))
    for i, dirn in enumerate(((0.0, -1.0, 0.25), (0.85, -0.45, 0.20))):
        ch = os.path.join(sortie, "_guepard_tete_%d.png" % i)
        A.photo(ch, tete + Vector(dirn).normalized() * (0.75 * L), tete, 46, (960, 720), 48, tete, 11.0)
        img.paste(Image.open(ch).convert("RGB"), (960 * i, 0))
        os.remove(ch)
    img.save(os.path.join(sortie, "guepard_tete.png"))
    shutil.copy2(os.path.join(apercus, "animaux", "guepard.png"), os.path.join(sortie, "guepard_apres.png"))
    print("[guepard] gros plan :", os.path.join(sortie, "guepard_tete.png"), flush=True)


if __name__ == "__main__":
    import styles
    garde = {}

    def bati():
        garde["a"] = styles.construire("guepard", styles.style_de("guepard"), sys.modules[__name__])
        return garde["a"]
    K.planche(bati, "Guépard")
    gros_plan(garde["a"])


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py guepard). Les pivots suivent la géométrie du 6e dessin (haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.620                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.000, 0.592)),
    ('cou', 'corps', (0.000, -0.420, 0.600)),
    ('tete', 'cou', (0.000, -0.600, 0.735)),
    ('oreille_G', 'tete', (0.050, -0.630, 0.850)),
    ('patte_av_G', 'corps', (0.090, -0.410, 0.600)),
    ('patte_ar_G', 'corps', (0.100, 0.230, 0.600)),
    ('queue', 'corps', (0.000, 0.400, 0.620)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('oeil', 'tete'), ('iris', 'tete'), ('truffe', 'tete'), ('tete', 'tete'),
    ('interieur', 'oreille', True), ('oreille', 'oreille', True), ('cou', 'cou'),
    ('cuisse', 'patte_ar', True), ('pied_av', 'patte_av', True), ('pied_ar', 'patte_ar', True),
    ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('queue', 'queue'), ('corps', 'corps'),
    ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
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
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.169 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.330), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
