"""L'émeu en peluche de velours ras, 4e dessin, essai 2 (19/10, refait sur la base gonflée ; le 3e : emeu_avant_1019 dans le
scratchpad de l'agent, refusé par l'auteur : « cou en tube »). Méthode : ANATOMIE (la référence CC-BY reçue,
references_3d/emeu, est un personnage de dessin animé appelé « Emu », une fille en robe en pose en T, vue le 19/10 :
rien à en tirer). Les mèches sont le geste du bœuf musqué : des mèches plates fondues dans la peau.

Les 5 traits de l'espèce : 1. un corps ovale haut perché, couvert de plumes brun-gris ébouriffées qui pendent comme
une serpillière, avec la raie au milieu du dos ; 2. un long cou fin qui s'affine vers la tête, emplumé de sombre en bas,
la peau nue bleutée sur la gorge ; 3. une petite tête sombre au bec court, large et plat, l'œil brun-orangé ; 4. de
longues pattes grises et fortes, la cheville pliée en arrière ; 5. trois gros doigts devant, griffus. Pas de casque,
pas de queue visible, les ailes cachées dans le plumage.

    python emeu.py        fabrique la fiche art/apercus/animaux/emeu.png (velours ras, palier 3)
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
import outils_a as O

GONFLAGE = True                               # la base gonflée : les mèches fondues dans une seule peau (le bœuf musqué)
GONFLAGE_REGLAGES = {"pression": 0.12, "fins": 0.0, "pointes": 0.0}   # haut sur pattes ; pointes 0 : le bout des mèches
                                              # reste effilé (fermé en boule, il ferait des boudins)

ENCRE = np.array(M.hexa("#7d6e60"))           # la dominante : brun-gris (registre)
SOMBRE = np.array(M.hexa("#6a5c50"))          # les mèches plus sombres (essai 2 : moins tranchées, l'essai 1 faisait des rayures)
CLAIR = np.array(M.hexa("#8e7f6e"))           # quelques mèches plus claires, pour le désordre
POINTE = np.array(M.hexa("#4e433b"))          # le bout des plumes, presque noir (le moucheté de l'émeu)
FONCE = np.array(M.hexa("#4e443c"))           # le cou emplumé, la nuque
BLEU = np.array(M.hexa("#8fb4d4"))            # la peau nue de la gorge
VISAGE = np.array(M.hexa("#7f95a8"))          # les joues : un gris bleuté (l'œil s'y détache)
CRANE = np.array(M.hexa("#3f3833"))           # le dessus de la tête, sombre
PATTE = np.array(M.hexa("#8a8680"))           # les pattes : gris
BEC = M.hexa("#3a3036")                       # le bec : charbon
GRIFFE = M.hexa("#35302c")
OEIL = M.hexa("#b0602a")                      # l'iris brun-orangé

CORPS = Vector((0.0, 0.040, 0.860))
DEMI = (0.215, 0.360, 0.250)                  # le corps : plus long que haut, plus haut que large
INCLINE = -8.0                                # le poitrail un peu relevé, la croupe qui descend


def meche(chemin, normales, large, plat=0.38, cotes=14, pas=6):
    """Une mèche plate couchée le long d'un chemin (le geste du bœuf musqué), sa face à plat contre la normale donnée à
    chaque point du chemin : elle épouse le dos, puis pend. Rend la maille et la fraction de chaque point (0 à la racine)."""
    p = A.courbe(chemin, pas)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    s_ctrl = fait[[i * pas for i in range(len(chemin))]]
    N = np.asarray(normales, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.maximum(np.linalg.norm(t, axis=1, keepdims=True), 1e-9)
        n = np.stack([np.interp(s, s_ctrl, N[:, k]) for k in range(3)], axis=-1)
        x = np.cross(n, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.60 * large, 0.05 * L), (0.95 * large, 0.22 * L), (large, 0.42 * L), (0.72 * large, 0.70 * L),
                     (0.30 * large, 0.93 * L), (0.06 * large, 0.985 * L), (0, L)], 5)
    m = A.tour(prof, cotes).etire(1.0, plat, 1.0)
    f = np.clip(m.v[:, 2] / L, 0.0, 1.0)
    return m.sculpte(couche), f


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=36, pas=0.006):
    """Une pièce tournée finement échantillonnée (fraction, rayon), couchée ensuite le long d'une courbe ; les deux bouts
    se referment en calotte arrondie (le cou du flamant rose gardé)."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 7)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def construire():
    a = K.Animal("emeu")
    a.taille = 1.80
    a.gonflage_reglages = dict(GONFLAGE_REGLAGES)            # lu aussi quand la fiche est lancée par un autre script
    rng = np.random.default_rng(19)

    # ----- le corps : un œuf haut perché, le dos bombé derrière le milieu, le poitrail plein, la croupe qui retombe -----
    def oeuf(v):
        v = K.bosse(v, (0, 0.35, 1.0), 0.10, 0.45)
        v = K.bosse(v, (0, -1.0, 0.1), 0.06, 0.30)
        v = K.bosse(v, (0, 0.9, -0.5), 0.05, 0.35)
        return v * list(DEMI)
    corps = A.boule(1.0, 56, 28).sculpte(oeuf)
    corps.teinte = np.tile(ENCRE, (len(corps.v), 1))
    RC = A.repere(CORPS, (INCLINE, 0, 0))
    RC3 = RC.to_3x3()
    a.piece("corps", corps, None, mat=RC)

    # ----- le plumage : des mèches plates nées de la raie du dos, couchées sur les flancs, qui pendent sous le ventre,
    #       en trois rangs qui se chevauchent ; des longueurs inégales, le bout qui s'écarte (ébouriffé) -----
    def sur_corps(beta, phi, cote, dehors):
        d = RC3 @ Vector((cote * math.sin(phi) * math.cos(beta), math.sin(beta), math.cos(phi) * math.cos(beta)))
        p, n = a.surface("corps", CORPS, d)
        return np.array(p + n * dehors), np.array(n)

    plumage = None
    for rang, (phi_a, phi_b, nombre) in enumerate(((0.03, 0.40, 15), (0.45, 0.95, 15), (1.00, 1.45, 13))):
        for cote in (1, -1):
            for i in range(nombre):
                yf = -0.90 + 1.84 * (i + rng.uniform(0.1, 0.9)) / nombre
                beta = math.asin(max(-0.97, min(0.97, yf)))
                phi0 = rng.uniform(phi_a, phi_b)
                phi1 = rng.uniform(1.80, 2.00)
                large = rng.uniform(0.040, 0.056)
                dehors = 0.30 * large * 0.38 * 2
                k = max(2, int((phi1 - phi0) / 0.30) + 1)
                chemin, normales = [], []
                for j in range(k + 1):
                    phi = phi0 + (phi1 - phi0) * j / k + rng.normal(0.0, 0.02)
                    p, n = sur_corps(beta + rng.normal(0.0, 0.015), phi, cote, dehors)
                    chemin.append(p)
                    normales.append(n)
                p_bas, n_bas = chemin[-1], normales[-1]
                h = np.array([n_bas[0], n_bas[1], 0.0])
                h /= max(np.linalg.norm(h), 1e-6)
                cote_t = np.cross(np.array([0.0, 0.0, 1.0]), h)
                z_fin = CORPS.z - DEMI[2] - rng.uniform(0.05, 0.13) - (0.04 if beta > 0.9 else 0.0)
                pend = max(0.08, float(p_bas[2] - z_fin))
                chemin.append(p_bas + h * 0.016 + np.array([0.0, 0.0, -0.40 * pend]) + cote_t * rng.normal(0.0, 0.008))
                chemin.append(p_bas + h * rng.uniform(0.040, 0.095) + np.array([0.0, 0.0, -pend]) + cote_t * rng.normal(0.0, 0.028))
                normales += [h, h]
                m, f = meche(chemin, normales, large)
                fond = (ENCRE, SOMBRE, CLAIR)[int(rng.integers(0, 3)) if rang else int(rng.integers(0, 2))]
                bout = K.lisse((f - 0.60) / 0.40)[:, None] * 0.45
                m.teinte = fond[None, :] * (1 - bout) + POINTE[None, :] * bout
                plumage = m if plumage is None else plumage + m
    a.piece("plumage", plumage, None)

    # ----- le cou : long et fin, épais à la base, qui s'affine vers la tête en S doux ; ovale (plus profond que large),
    #       la poche de la gorge un peu renflée en bas devant ; emplumé de sombre en bas, la peau bleue nue sur la gorge -----
    chemin_cou = [(0.0, -0.250, 0.990), (0.0, -0.318, 1.120), (0.0, -0.360, 1.270), (0.0, -0.372, 1.410), (0.0, -0.356, 1.530)]
    enc = K.Fil(chemin_cou, (1, 0, 0))
    Lc = enc.long
    # (essai 2 : à l'essai 1, le haut du cou était presque aussi large que la tête et tout bleu devant : un tube) : il
    # s'affine franchement jusque sous la tête, et le bleu n'est plus que sur la gorge, dans la moitié haute
    profil_cou = [(0.0, 0.130), (0.10, 0.105), (0.25, 0.080), (0.45, 0.058), (0.65, 0.043), (0.85, 0.035), (0.94, 0.036), (1.0, 0.044)]
    cou = fuseau(profil_cou, Lc, 36)

    def forme_cou(v):
        s = v.copy()
        fz = s[:, 2] / Lc
        s[:, 0] *= 0.88                                                            # ovale
        poche = np.exp(-((fz - 0.30) / 0.11) ** 2)
        s[:, 1] = np.where(s[:, 1] < 0, s[:, 1] * (1 + 0.20 * poche), s[:, 1])     # la gorge renflée, devant (-Y : le devant)
        return s
    cou.sculpte(forme_cou)
    fz = np.clip(cou.v[:, 2] / Lc, 0.0, 1.0)
    rr = np.maximum(np.hypot(cou.v[:, 0], cou.v[:, 1]), 1e-9)
    devant = K.lisse((-cou.v[:, 1] / rr + 0.20) / 0.85)                             # 0 sur la nuque et les côtés, 1 sur la gorge
    nu = K.lisse((fz - 0.48) / 0.16) * devant
    bas_ = K.lisse((0.35 - fz) / 0.35)
    plume = FONCE[None, :] * (1 - bas_[:, None]) + ENCRE[None, :] * bas_[:, None]
    cou.teinte = plume * (1 - nu[:, None]) + BLEU[None, :] * nu[:, None]
    a.piece("cou", cou.sculpte(enc.couche), None)

    # la moitié basse du cou emplumée : des mèches qui retombent sur le poitrail, tout autour, de plus en plus rares en
    # montant (le cou s'épaissit en bas, s'affine en haut) ; et quelques-unes le long de la nuque
    mches = None
    for i in range(46):
        fr = 0.02 + 0.52 * rng.uniform(0.0, 1.0) ** 1.3 if i < 38 else rng.uniform(0.50, 0.72)
        th = rng.uniform(-math.pi, math.pi) if i < 38 else rng.uniform(-0.5, 0.5)   # les dernières : sur la nuque seulement
        centre, avant, nuque = enc.cadre(fr * Lc)
        centre, avant, nuque = np.asarray(centre), np.asarray(avant), np.asarray(nuque)
        flanc = np.cross(nuque, avant)
        d = nuque * math.cos(th) + flanc * math.sin(th)
        r = float(np.interp(fr, *zip(*profil_cou)))
        long_ = rng.uniform(0.10, 0.17) if i < 38 else rng.uniform(0.06, 0.09)
        large = rng.uniform(0.026, 0.036) if i < 38 else 0.022
        p0 = centre + d * r * 0.80
        p1 = p0 - avant * long_ * 0.45 + d * 0.012
        p2 = p0 - avant * long_ * 0.80 + d * 0.022 + np.array([0.0, 0.0, -0.25 * long_])
        m, f = meche([p0, p1, p2], [d, d, d], large, 0.40, 12, 5)
        bout = K.lisse((f - 0.5) / 0.5)[:, None] * 0.5
        fond = ENCRE if fr < 0.25 else FONCE
        m.teinte = fond[None, :] * (1 - bout) + POINTE[None, :] * bout
        mches = m if mches is None else mches + m
    a.piece("plumes_cou", mches, None)

    # ----- la tête : petite, ronde, le crâne sombre, les joues gris bleuté ; le bec court, large et plat -----
    centre, avant, nuque = enc.cadre(Lc)
    HC = Vector(centre) + Vector((0.0, -0.030, 0.035))
    H = A.cadre(HC, Vector((0.0, -1.0, -0.10)).normalized(), Vector((0, 0, 1)))

    def crane(v):
        s = K.bosse(v, (0, 0.25, -1.0), 0.12, 0.40)                                # l'arrière du crâne
        s = K.bosse(s, (0, -0.7, 0.5), 0.06, 0.30)                                 # le menton, la gorge
        return s * [0.061, 0.058, 0.072]                                           # essai 2 : un peu plus grosse (peluche)
    tete = A.boule(1.0, 40, 20)
    u = tete.v.copy()
    dessus = np.maximum(K.lisse((u[:, 1] - 0.10) / 0.55), 0.8 * K.lisse((-u[:, 2] + 0.15) / 0.70))
    tete.teinte = VISAGE[None, :] * (1 - dessus[:, None]) + CRANE[None, :] * dessus[:, None]
    a.piece("tete", tete.sculpte(crane), None, mat=H)
    a.tete = H @ Vector((0.0, 0.0, 0.020))
    bec = A.tour(A.profil([(0, 0), (0.030, 0.006), (0.031, 0.030), (0.026, 0.058), (0.016, 0.078), (0, 0.086)], 6), 32)
    bec.sculpte(lambda v: np.stack([v[:, 0], v[:, 1] - 0.22 * (np.clip(v[:, 2] - 0.04, 0, None) / 0.046) ** 2 * 0.020, v[:, 2]], axis=1))
    a.piece("bec", bec.etire(1.0, 0.52, 1.0), BEC, mat=H @ A.repere((0, -0.014, 0.046)), poil=False)

    # deux yeux ronds et ouverts, un mince iris brun-orangé autour, visibles de face comme de trois quarts (essai 2 : plus
    # petits, plus en avant, l'anneau plus fin ; à l'essai 1 ils débordaient de la tête de face, comme des lunettes)
    direction_g = (0.56, 0.24, 0.68)
    for nom, c in (("G", 1), ("D", -1)):
        regard = H.to_3x3() @ Vector((c * direction_g[0], direction_g[1], direction_g[2]))
        a.rustine("iris_" + nom, "tete", HC, regard, 0.38, OEIL, 0.003, 0)
    O.paire_yeux(a, "tete", HC, direction_g, 0.0190, decolle=0.004, R=H)

    # ----- les pattes : longues et fortes, le pilon caché sous les plumes, la cheville pliée en arrière, le tarse gris ;
    #       trois gros doigts devant, chacun sa griffe -----
    for nom, c in (("G", 1), ("D", -1)):
        pts = [(c * 0.095, 0.050, 0.760), (c * 0.102, 0.092, 0.585), (c * 0.108, 0.135, 0.420), (c * 0.108, 0.105, 0.240),
               (c * 0.108, 0.060, 0.070)]
        jambe = O.membre(pts, [0.078, 0.064, 0.054, 0.043, 0.040], [(0.30, ENCRE), (1.0, PATTE)], 18)   # essai 2 : plus fortes
        a.piece("jambe_" + nom, jambe, None, poil=False)
        F = np.array((c * 0.108, 0.052, 0.030))
        pied = A.boule(1.0, 24, 12).etire(0.047, 0.050, 0.029)
        pied.teinte = np.tile(PATTE, (len(pied.v), 1))
        a.piece("pied_" + nom, pied, None, pos=tuple(F), poil=False)
        for k, (ang, long_) in enumerate(((c * 4.0, 0.135), (c * 32.0, 0.105), (-c * 26.0, 0.100))):
            t = math.radians(ang)
            dirn = np.array((math.sin(t), -math.cos(t), 0.0))
            r0, r1 = 0.025, 0.016
            racine = F + dirn * 0.010
            milieu = F + dirn * long_ * 0.55 + np.array((0.0, 0.0, r0 * 0.85 - F[2] + 0.004))
            bout = F + dirn * long_ + np.array((0.0, 0.0, r1 - F[2]))
            orteil = A.tube(A.courbe([tuple(racine), tuple(milieu), tuple(bout)], 6), lambda q: r0 + (r1 - r0) * q, 14)
            orteil.teinte = np.tile(PATTE, (len(orteil.v), 1))
            a.piece("orteil_%s%d" % (nom, k), orteil, None, poil=False)
            g = O.griffe(0.030, 0.0105)
            pos = bout + dirn * (r1 * 0.55)
            a.piece("griffe_%s%d" % (nom, k), g, GRIFFE, mat=A.cadre(Vector(tuple(pos)), Vector(tuple(dirn + np.array((0.0, 0.0, -0.25))))),
                    poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("emeu", styles.style_de("emeu"), sys.modules[__name__]), "Émeu")
