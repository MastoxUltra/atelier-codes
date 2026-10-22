"""Le gnou en peluche de velours ras : un gris argent bleuté, la face allongée et noire, une barbe et une crinière
noires hérissées, des cornes en crochets qui partent sur le côté puis se relèvent, le garrot haut et la croupe basse, le
cou épais rayé de fines bandes sombres, de longues jambes fines, la queue en crin noir. Le clown triste de la plaine :
la tête baissée en avant, les cornes pointées devant lui, un œil par en dessous, un antérieur en avant : il va faire
semblant de charger.

    python gnou.py        fabrique la fiche art/apercus/animaux/gnou.png (velours ras, palier 3)
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


ARGENT = np.array(M.hexa("#70747f"))          # la dominante : gris foncé ardoise (blanc-bleu, on ne lisait pas le gnou : 16/10)
BANDE = np.array(M.hexa("#3e4250"))           # les bandes du cou et des épaules
NOIR = np.array(M.hexa("#2e2c34"))            # le museau, la barbe, la crinière, la queue
CORNE = M.hexa("#d0c4a4")
OEIL = M.hexa("#c08a3a")
MUFLE = np.array(M.hexa("#8a8492"))           # le bout du museau, plus clair (3e essai)
PAS = 0.008


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    # les deux bouts de la pièce se referment en calotte arrondie (plus de cylindre coupé net)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("gnou")
    a.taille = 2.00

    # ----- le corps : le garrot haut, la croupe basse, le poitrail profond ; des bandes sombres sur l'avant -----
    # (18/10, 4e essai, d'après les vues de la référence : debout, le dos qui descend du garrot vers la croupe, le corps
    # plus épais et plus bas sur des pattes fines à genoux et jarrets marqués, la tête à hauteur d'épaule)
    fil = K.Fil([(0.0, y, z) for y, z in ((0.460, 0.640), (0.280, 0.680), (0.020, 0.750), (-0.200, 0.820), (-0.340, 0.840))], (1, 0, 0))
    L = fil.long
    corps = fuseau([(0.0, 0.0), (0.04, 0.130), (0.15, 0.200), (0.45, 0.220), (0.75, 0.250), (0.92, 0.240), (1.0, 0.0)], L, 72)
    z = corps.v[:, 2]
    th = np.abs(np.arctan2(corps.v[:, 0], corps.v[:, 1]))
    t = np.tile(ARGENT, (len(z), 1))
    bande = (((z - 0.55 * L) / 0.062) % 1.0 < 0.34) & (z > 0.55 * L) & (th < 2.2 * (1.0 - 0.35 * (z - 0.55 * L) / (0.45 * L)))
    t[bande] = BANDE
    corps.teinte = t
    a.piece("corps", corps.sculpte(fil.couche), None)
    # (5e essai, 19/10 : les six pointes noires du garrot, fondues et gonflées, faisaient une crête de dinosaure) : la
    # crinière est une seule brosse noire continue, de la nuque au garrot, plus bas sur le cou (voir plus bas)

    # ----- le cou et la tête : un cou épais, la tête basse tournée vers nous ; une face longue et noire, la barbe ; les cornes -----
    COU = [(0.0, -0.240, 0.860), (0.0, -0.400, 0.950), (0.0, -0.520, 0.990)]
    a.piece("cou", A.tube(A.courbe(COU, 5), lambda t: 0.180 - 0.058 * t, 22), tuple(ARGENT))
    # (16/10, repris par Art : en gros plan, le museau rond, pointé sur nous, cachait les yeux) : la tête longue PENDUE vers
    # l'avant et le bas, comme la référence (references_3d/gnou, CC-BY : vues seulement) ; un peu tournée vers nous. Les yeux,
    # en haut de la face près des cornes, restent au-dessus du museau de face comme de trois quarts
    # (3e essai, refusé : « de face, une grosse chaussette sombre, les yeux en fentes derrière les cornes ») : la tête un peu
    # moins basse (on voit la face) ; de GROS yeux de peluche sur le front, au-dessus du museau, sous une paupière à 0,62 ;
    # un museau large et carré, plus clair au bout, deux narines ; la barbe sombre sous la gorge, une crinière courte sur la nuque
    # (4e essai : « la tête pend jusqu'au sol, la face trop ronde ») : la tête à hauteur d'épaule, la face LONGUE et
    # étroite, presque verticale comme chez le vrai, qui s'élargit au museau ; un peu tournée vers nous
    # (5e essai, 19/10 : la tête pendait encore sous le poitrail, de face « une chaussette », les yeux de face sous des
    # paupières noires qui leur donnaient l'air fâché) : la tête PORTÉE à hauteur d'épaule, la nuque au niveau du garrot, la
    # face inclinée à 45° vers l'avant et le bas (le museau à hauteur du coude, plus jamais sous le poitrail) ; la face plus
    # large que profonde, le chanfrein plat ; les yeux sur les CÔTÉS de la tête, sous la base des cornes, sans paupière lourde
    AVANT_T = Vector((0.22, -0.64, -0.73)).normalized()
    H = A.cadre(Vector((0.0, -0.610, 0.940)), AVANT_T, Vector((0, 0, 1)))
    H3 = H.to_3x3()
    tete = fuseau([(0.0, 0.0), (0.06, 0.095), (0.20, 0.110), (0.45, 0.082), (0.72, 0.076), (0.90, 0.092), (1.0, 0.0)], 0.520, 56, 0.007)
    tete.etire(1.10, 0.92, 1.0)                                         # la face plus large que profonde
    tete.teinte = np.tile(NOIR, (len(tete.v), 1))
    a.piece("tete", tete, None, mat=H @ A.repere((0, 0.020, -0.130)))
    # le museau : large et carré, à peine plus clair au bout (le bout gris clair faisait le bout d'une chaussette) ; deux narines
    museau = A.boule(1.0, 36, 18).sculpte(lambda v: K.emousse(v, 0.62)).etire(0.100, 0.074, 0.070)
    museau.teinte = np.tile(NOIR * 1.15, (len(museau.v), 1))
    museau.teinte[museau.v[:, 2] > 0.25 * 0.070] = NOIR * 1.45
    a.piece("museau", museau, None, mat=H @ A.repere((0, -0.004, 0.345)))
    for nom_n, c in (("G", 1), ("D", -1)):
        pn, nn = a.surface("museau", H @ Vector((0, -0.004, 0.345)), H3 @ Vector((c * 0.42, 0.10, 0.90)))
        a.piece("narine_" + nom_n, A.boule(1.0, 14, 7).etire(0.010, 0.015, 0.005), tuple(NOIR * 0.45),
                mat=A.cadre(pn + nn * 0.001, nn, H3 @ Vector((c * 0.30, 1.0, 0.0))), poil=False)
    # la barbe (5e essai : une seule touffe cachée derrière la mâchoire) : une frange noire qui pend sous la gorge et tout
    # le dessous du cou, jusqu'au haut du poitrail, comme chez le gnou bleu
    gorge = H @ Vector((0.0, -0.075, -0.030))
    trajet = [gorge, Vector((0.0, -0.450, 0.820)), Vector((0.0, -0.340, 0.730))]
    barbe = None
    for k, f in enumerate(np.linspace(0.0, 1.0, 7)):
        q = trajet[0].lerp(trajet[1], min(f * 2.0, 1.0)) if f <= 0.5 else trajet[1].lerp(trajet[2], (f - 0.5) * 2.0)
        long_ = 0.055 + 0.022 * math.sin(math.pi * f)                   # plus longue au milieu du cou
        m = A.boule(1.0, 16, 8).etire(0.022, 0.040, long_)
        m.v[:, 2] -= long_ * 0.40                                      # elle pend sous le point (8 à 11 cm)
        m.v = m.v + np.array([q.x, q.y, q.z])
        barbe = m if barbe is None else barbe + m
    a.piece("barbe", barbe, tuple(NOIR))
    # la crinière : une brosse noire CONTINUE, dressée sur le dessus du cou, de la nuque jusqu'au garrot (des mèches serrées
    # qui se recouvrent : fondues, elles font une seule crête souple)
    nuque = H @ Vector((0.0, 0.070, -0.110))
    crin_trajet = [nuque, Vector((0.0, -0.440, 1.080)), Vector((0.0, -0.300, 1.050)), Vector((0.0, -0.170, 1.040))]
    crin = None
    pts_c = A.courbe([tuple(p) for p in crin_trajet], 8)
    for k in range(0, len(pts_c), 2):
        q = Vector(pts_c[k])
        tg = Vector(pts_c[min(k + 1, len(pts_c) - 1)]) - Vector(pts_c[max(k - 1, 0)])
        if tg.length < 1e-6:
            continue
        haut_m = 0.045 + 0.012 * math.sin(math.pi * k / max(len(pts_c) - 1, 1))
        m = A.boule(1.0, 12, 6).etire(0.017, 0.034, haut_m)
        m.v[:, 2] += haut_m * 0.35                                     # elle se dresse au-dessus du point
        r_ = np.array(A.cadre(q, Vector((0, 0, 1)), tg))
        m.v = m.v @ r_[:3, :3].T + r_[:3, 3]
        crin = m if crin is None else crin + m
    a.piece("criniere", crin, tuple(NOIR))
    a.tete = H @ Vector((0, 0.020, 0.200))
    a.cap_tete = Vector((AVANT_T.x, AVANT_T.y, 0.0)).normalized()     # la vue de près, de trois quarts devant la tête
    a.fusion_a_part = ("narine",)
    # (5e essai) aucun bout fermé en boule : au 4e, les deux oreilles avaient été raccourcies de 96 mm en moignons ronds
    # (journal du 18/10, « pointes 60 mm : raccourcie de 96 mm ») ; le reste du réglage est celui des bêtes hautes sur pattes
    a.gonflage_reglages = {"pression": 0.12, "fins": 0.0, "pointes": 0.0}
    R_OEIL = 0.027
    for nom, c in (("G", 1), ("D", -1)):
        # sur les côtés de la tête, en haut, sous la base de la corne : de face, ils dépassent du bord de la face ; de trois
        # quarts, on les voit entiers ; ouverts, sans paupière lourde (5e essai)
        pos, n = a.surface("tete", H @ Vector((0, 0.005, 0.075)), H3 @ Vector((c * 0.80, 0.50, 0.12)))
        a.oeil("oeil_" + nom, pos + n * 0.003, n, R_OEIL)
        # la corne : part sur le côté, descend, puis se relève en crochet
        ch = [H @ Vector(q) for q in ((c * 0.060, 0.080, -0.010), (c * 0.130, 0.085, -0.012), (c * 0.200, 0.055, -0.020), (c * 0.236, -0.005, -0.026), (c * 0.226, -0.062, -0.032), (c * 0.196, -0.040, -0.040), (c * 0.170, 0.050, -0.046))]
        a.piece("corne_" + nom, A.tube(A.courbe(propres(ch), 6), lambda t: 0.034 - 0.026 * t, 14), CORNE, poil=False)
        # l'oreille : en feuille un peu pointue, portée à l'horizontale sur le côté, sous la corne (5e essai : dressée, ronde,
        # elle faisait une oreille de souris)
        po = A.profil([(0, 0), (0.030, 0.008), (0.036, 0.030), (0.026, 0.058), (0.010, 0.078), (0, 0.086)], 5)
        a.piece("oreille_" + nom, A.tour(po, 24).etire(1.0, 0.38, 1.0), tuple(ARGENT),
                mat=A.cadre(H @ Vector((c * 0.090, 0.040, -0.085)), H3 @ Vector((c * 0.95, -0.12, -0.18)), H3 @ Vector((0.0, 1.0, 0.0))))

    # ----- les jambes : fines et longues, le genou marqué, les sabots noirs ; l'antérieur gauche avancé -----
    # (5e essai : le genou en bosse étroite (+14 %) faisait des saucisses bosselées une fois gonflé ; un genou doux, un canon
    # fin et droit, et de vrais sabots fendus, plus larges que le paturon, au lieu de petites boules noires)
    def sabot():
        """Un sabot de bovidé : un cône bas arrondi, plus large au sol, un peu plus long que large, fendu devant."""
        m = A.tour(A.profil([(0.0, 0.0), (0.046, 0.0), (0.048, 0.012), (0.044, 0.036), (0.037, 0.054), (0.0, 0.060)], 4), 28)
        m.etire(1.0, 1.15, 1.0)

        def fente(v):
            s_ = v.copy()
            devant = np.clip(-v[:, 1] / 0.050, 0.0, 1.0)
            s_[:, 1] += 0.010 * np.exp(-(v[:, 0] / 0.006) ** 2) * devant
            return s_
        return m.sculpte(fente)

    def jambe(pts, r0, avant=True):
        ft = K.Fil(pts, (1, 0, 0))
        if avant:                                    # le genou aux deux tiers, à peine plus large ; le canon fin
            prof = [(0.0, r0), (0.28, r0 * 0.70), (0.50, r0 * 0.56), (0.58, r0 * 0.60), (0.68, r0 * 0.46), (0.92, r0 * 0.40), (1.0, 0.0)]
        else:                                        # la cuisse forte, le jarret doux, le canon fin
            prof = [(0.0, r0), (0.30, r0 * 0.80), (0.50, r0 * 0.56), (0.57, r0 * 0.58), (0.66, r0 * 0.44), (0.92, r0 * 0.38), (1.0, 0.0)]
        m = fuseau(prof, ft.long, 28, 0.008)
        m.teinte = np.tile(ARGENT, (len(m.v), 1))
        return m.sculpte(ft.couche)
    for nom, pts, r0 in (("av_D", [(-0.110, -0.240, 0.780), (-0.115, -0.225, 0.560), (-0.115, -0.205, 0.330), (-0.115, -0.240, 0.040)], 0.085),
                         ("av_G", [(0.110, -0.240, 0.780), (0.115, -0.225, 0.560), (0.115, -0.205, 0.330), (0.115, -0.240, 0.040)], 0.085),
                         ("ar_G", [(0.120, 0.380, 0.690), (0.130, 0.330, 0.480), (0.130, 0.440, 0.260), (0.130, 0.400, 0.040)], 0.095),
                         ("ar_D", [(-0.120, 0.380, 0.690), (-0.130, 0.330, 0.480), (-0.130, 0.440, 0.260), (-0.130, 0.400, 0.040)], 0.095)):
        a.piece("jambe_" + nom, jambe(pts, r0, nom.startswith("av")), None)
        a.piece("sabot_" + nom, sabot(), tuple(NOIR), pos=(pts[-1][0], pts[-1][1] - 0.010, 0.0), poil=False)
    chemin = [(0.0, 0.470, 0.730), (0.0, 0.560, 0.660), (0.0, 0.600, 0.480), (0.010, 0.590, 0.320)]
    a.piece("queue", K.tube_peint(A.courbe(chemin, 6), lambda t: 0.020 + 0.034 * t, [(1, tuple(NOIR))], 14), None)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("gnou", styles.style_de("gnou"), sys.modules[__name__]), "Gnou")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py gnou). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.780                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.100, 0.740)),
    ('cou', 'corps', (0.000, -0.240, 0.860)),
    ('tete', 'cou', (0.000, -0.550, 1.000)),            # (5e essai, 19/10 : la tête portée plus haut)
    ('oreille_G', 'tete', (0.076, -0.554, 1.030)),
    ('patte_av_D', 'corps', (-0.110, -0.240, 0.780)),
    ('patte_ar_G', 'corps', (0.120, 0.380, 0.690)),
    ('patte_av_G', 'corps', (0.110, -0.240, 0.780)),
    ('queue', 'corps', (0.000, 0.470, 0.730)),
]

PORTEURS = [
    ('criniere_cou', 'cou'), ('oeil_reflet', 'tete'), ('jambe_av', 'patte_av', True), ('jambe_ar', 'patte_ar', True), ('criniere', 'cou'),
    ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True), ('oreille', 'oreille', True), ('museau', 'tete'), ('narine', 'tete'), ('lourde', 'tete'),
    ('corps', 'corps'), ('queue', 'queue'), ('barbe', 'tete'), ('corne', 'tete'), ('tete', 'tete'), ('iris', 'tete'),
    ('oeil', 'tete'), ('cou', 'cou'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
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
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.234 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
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
    p.add('corps', pos=(0, 0, -0.429), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('cou', rot=(30, 0, 44))
    p.add('tete', rot=(14, 4, 28))
    p.paire('oreille', rot=(-24, 0, 0))
    p.add('queue', rot=(6, 0, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
