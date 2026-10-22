"""Le pangolin en peluche (3e dessin, 19/10, d'après les VUES de sa référence CC-BY references_3d/pangolin : rien n'en
est importé, on en a tiré les proportions). l'auteur, 19/10 : « il est bien, mais fais-le aussi avec le modèle ».

Les proportions de la référence (en part de sa longueur, de la queue au nez) : un corps rond et haut en dôme (le dos à
0,70, le ventre à 0,16 du sol, 0,50 de large), une petite tête en cône basse devant (0,15 de long, le nez à 0,27 du sol),
une queue épaisse à la base qui s'effile jusqu'au sol, quatre pattes courtes et fortes sous le corps (celles de devant
penchées en avant), tout le dessus couvert de grandes écailles arrondies posées en quinconce.

Les 5 traits qui font le pangolin : 1. une armure de grandes écailles en tuiles qui se recouvrent, de la nuque au bout
de la queue ; 2. un corps rond en dôme, le dos voûté ; 3. une petite tête pointue, le visage nu et clair ; 4. une
longue queue épaisse et écailleuse qui traîne au sol ; 5. des pattes courtes aux grandes griffes de fouisseur, le ventre
doux sans écailles.

Les écailles sont des PIÈCES DURES à part (pas des bosses peintes) : chacune une tuile lisse et épaisse, bombée, posée
sur la peau, la racine vers la tête, le bord libre relevé vers la queue par-dessus la racine de la rangée suivante.
Elles restent à part de la peau fondue (a.fusion_a_part) et suivent le gonflage.

    python pangolin.py        fabrique la fiche art/apercus/animaux/pangolin.png
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
TUILE = np.array(M.hexa("#e8844e"))           # la dominante : les écailles terre cuite
TUILE_BRUN = np.array(M.hexa("#8e4a2c"))      # la peau sous les écailles et leur dessous : l'ombre entre les tuiles
DORE = np.array(M.hexa("#ffc46a"))            # l'accent : le bord libre des écailles, doré
PEAU = np.array(M.hexa("#c87a52"))            # les pattes
CREME = np.array(M.hexa("#fff0d8"))           # le ventre et le visage
CHARBON = M.hexa("#3e302c")                   # les griffes, le nez
PAS = 0.005
TOUR_TETE = 12.0                              # la tête tournée vers la caméra de la fiche (degrés) : les deux yeux vus ensemble


def lisser(r, n=5):
    k = np.ones(n) / n
    return np.convolve(np.pad(r, n // 2, mode="edge"), k, "valid")


def fuseau(points, longueur, cotes=64, pas=PAS):
    """Une pièce tournée le long de Z : points = [(fraction, rayon)], les deux bouts refermés en calotte arrondie."""
    s = np.arange(pas, longueur - pas, pas)
    f, r = zip(*points)
    rayons = lisser(np.interp(s / longueur, f, r), 5)
    c0, c1 = max(float(r[0]) * 0.9, 0.004), max(float(r[-1]) * 0.9, 0.004)
    rayons = rayons * np.sqrt(np.clip(1.0 - (np.maximum(c0 - s, 0.0) / c0) ** 2, 0.0, 1.0)) * np.sqrt(np.clip(1.0 - (np.maximum(s - (longueur - c1), 0.0) / c1) ** 2, 0.0, 1.0))
    return A.tour([(0.0, 0.0)] + [(float(ri), float(si)) for ri, si in zip(rayons, s)] + [(0.0, float(longueur))], cotes)


def rayon_a(profil, f):
    fr, rr = zip(*profil)
    return float(np.interp(f, fr, rr))


def tuile(a_, b_, t_, courbe, releve):
    """Une écaille : une tuile lisse et épaisse, plus large que longue, la racine (y = -b) plus épaisse, le bord libre
    (y = +b) arrondi en pointe douce. Bombée pour épouser la peau en travers (courbe : le rayon de la peau), le bord libre
    relevé de « releve » radians. Repère : X en travers, Y vers la queue, Z hors de la peau. La teinte : le dessus terre
    cuite, le bord libre doré, le dessous dans l'ombre."""
    m = A.boule(1.0, 18, 8)
    x, y, z = m.v[:, 0].copy(), m.v[:, 1].copy(), m.v[:, 2].copy()
    arriere = np.clip(y, 0.0, 1.0)
    X = x * a_ * (1.0 - 0.20 * arriere ** 2)
    Y = y * b_ * np.where(y > 0, 1.10, 0.95)
    Z = z * t_ * (1.0 - 0.45 * (y + 1.0) / 2.0)
    Z = Z - X ** 2 / (2.0 * max(courbe, 1e-3))
    Z = Z + (Y + b_) * math.tan(releve)
    m.v = np.stack([X, Y, Z], axis=1)
    rho = np.sqrt(x ** 2 + y ** 2)
    t = np.tile(TUILE, (len(x), 1))
    bord = (z > -0.2) & (rho > 0.72) & (y > -0.35)
    t[bord] = DORE
    t[(z > -0.2) & (rho > 0.55) & (rho <= 0.72) & (y > -0.35)] = 0.5 * (TUILE + DORE)
    t[z < -0.35] = TUILE_BRUN
    m.teinte = t
    return m


def assembler(mailles):
    """Plusieurs mailles en une seule pièce (plus vite que des additions en chaîne)."""
    v, f, t, n = [], [], [], 0
    for m in mailles:
        v.append(m.v)
        f.extend(tuple(i + n for i in face) for face in m.f)
        t.append(m.teinte)
        n += len(m.v)
    out = A.Maille(np.vstack(v), f)
    out.teinte = np.vstack(t)
    return out


def armure(a, sur, fil, profil, debut, fin, ouverture, par_rang, releve=math.radians(13), vers_queue=1.0, plus=1.12):
    """Les écailles d'une pièce couchée le long d'un fil : des rangées de « par_rang » tuiles (en quinconce, une sur deux
    décalée d'une demi-tuile), de la fraction « debut » à « fin » du fil, sur « ouverture » radians de part et d'autre du
    dessus. Chaque tuile est posée là où un rayon parti du fil touche la peau de « sur ». vers_queue : +1 si le fil va de
    la tête vers la queue, -1 s'il va vers la tête. Rend la maille de toutes les tuiles."""
    L = fil.long
    tuiles = []
    s = debut * L
    rang = 0
    while s <= fin * L:
        R = rayon_a(profil, s / L)
        n = par_rang - (rang % 2)                         # quinconce : une rangée sur deux a une tuile de moins, décalée
        dth = 2.0 * ouverture / par_rang
        a_ = 0.5 * dth * R * plus
        b_ = a_ * 1.02
        t_ = max(0.0045, 0.17 * a_)
        centre, avant, nuque, flanc = fil._repere(s)
        for k in range(n):
            th = -ouverture + dth * (k + 0.5 + 0.5 * (rang % 2))
            d = nuque * math.cos(th) + flanc * math.sin(th)
            try:
                p, nrm = a.surface(sur, Vector(tuple(float(c_) for c_ in centre)), Vector(tuple(float(c_) for c_ in d)))
            except ValueError:
                continue
            p, nrm = np.array(p, float), np.array(nrm, float)
            nrm = nrm / max(np.linalg.norm(nrm), 1e-9)
            Y = np.asarray(avant, float) * vers_queue
            Y = Y - (Y @ nrm) * nrm
            if np.linalg.norm(Y) < 1e-6:
                continue
            Y = Y / np.linalg.norm(Y)
            X = np.cross(Y, nrm)
            courbe = max(float(np.linalg.norm(p - centre)), 0.02)
            m = tuile(a_, b_, t_, courbe, releve)
            origine = p + nrm * (-b_ * math.tan(releve) + 0.15 * t_)       # la racine rentre un peu dans la peau
            m.v = origine + m.v[:, 0:1] * X + m.v[:, 1:2] * Y + m.v[:, 2:3] * nrm
            tuiles.append(m)
        s += b_ * 1.05
        rang += 1
    return assembler(tuiles)


def couche(fil, maille, ecrase_haut=1.0, ecrase_bas=1.0, large=1.0):
    """Couche une pièce tournée le long du fil ; son dessous (vers -nuque) écrasé, son dessus aussi, ses flancs étirés."""
    v = maille.v
    v[:, 0] *= large
    v[:, 1] *= np.where(v[:, 1] > 0, ecrase_haut, ecrase_bas)
    return maille.sculpte(fil.couche)


def angle_dessus(maille_locale):
    """L'angle de chaque point depuis le dessus (0) vers le flanc (pi au ventre), dans le repère d'une pièce tournée."""
    return np.abs(np.arctan2(maille_locale[:, 0], maille_locale[:, 1]))


def construire():
    a = K.Animal("pangolin")
    a.taille = 1.00
    a.fusion_a_part = ("ecaille",)                    # les écailles : des pièces dures, posées sur la peau, jamais fondues

    # ----- le corps : un dôme rond et haut (la référence : le dos à 0,70, le ventre à 0,16, 0,50 de large), le ventre
    #       un peu aplati ; la peau sous les écailles brun d'ombre, le ventre crème et doux -----
    fil_c = K.Fil([(0.0, -0.300, 0.380), (0.0, -0.180, 0.415), (0.0, -0.020, 0.425), (0.0, 0.140, 0.405), (0.0, 0.270, 0.348)],
                  (1, 0, 0), haut=(0, 0, 1))
    Lc = fil_c.long
    prof_c = [(0.0, 0.150), (0.08, 0.190), (0.22, 0.245), (0.42, 0.272), (0.62, 0.266), (0.80, 0.236), (0.93, 0.190), (1.0, 0.140)]
    corps = fuseau(prof_c, Lc, 72)
    th = angle_dessus(corps.v)
    t = np.tile(TUILE_BRUN, (len(th), 1))
    t[th > math.radians(116)] = CREME
    corps.teinte = t
    a.piece("corps", couche(fil_c, corps, 1.0, 0.86, 0.94), None)

    # ----- la tête : un petit cône pointu, basse devant (le nez à 0,27 du sol), tournée un peu vers la caméra ; le visage
    #       nu et clair, le haut du crâne écaillé jusqu'au front -----
    base = np.array((0.0, -0.270, 0.420))

    def tete_pt(y, z):
        d = Vector((0.0, y - base[1], z - base[2]))
        d = A.tourne((0, 0, 1), TOUR_TETE, d)
        return (float(base[0] + d.x), float(base[1] + d.y), float(base[2] + d.z))
    fil_t = K.Fil([tete_pt(-0.270, 0.420), tete_pt(-0.400, 0.352), tete_pt(-0.525, 0.272)], (1, 0, 0), haut=(0, 0, 1))
    Lt = fil_t.long
    prof_t = [(0.0, 0.140), (0.15, 0.136), (0.35, 0.116), (0.55, 0.090), (0.75, 0.064), (0.90, 0.044), (1.0, 0.032)]
    tete = fuseau(prof_t, Lt, 56)
    tht = angle_dessus(tete.v)
    ft = tete.v[:, 2] / Lt
    tt = np.tile(CREME, (len(tht), 1))
    tt[(tht < math.radians(62)) & (ft < 0.47)] = TUILE_BRUN
    tete.teinte = tt
    a.piece("tete", couche(fil_t, tete, 1.0, 0.92, 0.95), None)

    # le nez : un petit bout sombre au bout du museau
    cn, avn, _nn = fil_t.cadre(Lt * 0.995)
    a.piece("nez", A.boule(1.0, 24, 12).etire(0.020, 0.017, 0.016), CHARBON,
            mat=A.cadre(Vector(tuple(np.array(cn) + np.array(avn) * 0.012)), Vector(tuple(avn)), Vector((0, 0, 1))), poil=False)

    # les yeux : deux boutons ouverts, de même taille, posés symétriques dans le repère de la TÊTE (tournée), vers l'avant
    ce, ave, nqe, fle = fil_t._repere(Lt * 0.52)
    for nom, c in (("G", 1), ("D", -1)):
        d = np.array(fle) * c * 0.64 + np.array(ave) * 0.55 + np.array(nqe) * 0.38
        p, n = a.surface("tete", Vector(tuple(ce)), Vector(tuple(d)))
        a.oeil("oeil_" + nom, p + n * 0.004, n, 0.0235)
    a.tete = Vector(tuple(fil_t.cadre(Lt * 0.60)[0]))
    cap = np.array(fil_t.cadre(Lt * 0.6)[1])
    a.cap_tete = Vector((float(cap[0]), float(cap[1]), 0.0)).normalized()

    # ----- la queue : longue, épaisse à la base, qui s'effile en traînant au sol et s'enroule un peu vers la caméra -----
    fil_q = K.Fil([(0.0, 0.180, 0.375), (0.0, 0.320, 0.310), (0.030, 0.440, 0.215), (0.080, 0.550, 0.118), (0.150, 0.640, 0.058),
                   (0.240, 0.700, 0.040)], (1, 0, 0), haut=(0, 0, 1))
    Lq = fil_q.long
    prof_q = [(0.0, 0.170), (0.15, 0.160), (0.35, 0.130), (0.55, 0.100), (0.75, 0.070), (0.90, 0.046), (1.0, 0.030)]
    queue = fuseau(prof_q, Lq, 56)
    thq = angle_dessus(queue.v)
    tq = np.tile(TUILE_BRUN, (len(thq), 1))
    tq[thq > math.radians(132)] = CREME
    tq[queue.v[:, 2] > 0.93 * Lq] = TUILE                                     # le bout de la queue : pas de peau claire
    queue.teinte = tq
    a.piece("queue", couche(fil_q, queue, 0.84, 0.80, 1.0), None)

    # ----- les pattes : courtes et fortes, sous le corps (devant : penchées en avant, comme sur la référence), chacune
    #       finit par un pied posé au sol ; de grandes griffes sombres et courbes (trois longues devant, quatre derrière) -----
    for nom, x_, ch in (("av_G", 0.130, [(0.130, -0.165, 0.270), (0.148, -0.205, 0.150), (0.155, -0.250, 0.052), (0.158, -0.292, 0.044)]),
                        ("ar_G", 0.135, [(0.135, 0.100, 0.270), (0.150, 0.098, 0.140), (0.155, 0.078, 0.052), (0.158, 0.034, 0.044)])):
        for cote, suffixe in ((1, nom), (-1, nom[:-1] + "D")):
            pts = [(cote * px, py, pz) for px, py, pz in ch]
            fl = K.Fil(pts, (1, 0, 0))
            m = fuseau([(0.0, 0.078), (0.35, 0.068), (0.62, 0.056), (0.82, 0.056), (1.0, 0.046)], fl.long, 28, 0.004)
            m.teinte = np.tile(PEAU, (len(m.v), 1))
            a.piece("patte_" + suffixe, m.sculpte(fl.couche), None)
            bout = np.array(pts[-1], float)
            avant_pied = np.array((0.0, -1.0, 0.0))
            devant = suffixe.startswith("av")
            griffes = []
            for k_, dx in enumerate((-1, 0, 1) if devant else (-1.5, -0.5, 0.5, 1.5)):
                long_ = (0.064 if dx == 0 else 0.052) if devant else 0.036
                g = A.tour(A.profil([(0, 0), (0.0095, 0.004), (0.0085, long_ * 0.20), (0.006, long_ * 0.55),
                                     (0.0025, long_ * 0.88), (0, long_)], 5), 10)
                g.sculpte(lambda v, L_=long_: v - np.c_[np.zeros(len(v)), 0.30 * (v[:, 2] / L_) ** 2 * L_, np.zeros(len(v))])
                pos = bout + avant_pied * 0.010 + np.array((dx * 0.020, 0.0, -0.016))    # la racine dans le bout du pied
                vise = Vector((dx * 0.10, -0.92, -0.38)).normalized()
                g.v = np.array([tuple(A.cadre(Vector(tuple(pos)), vise, Vector((0, 0, 1))) @ Vector(tuple(q))) for q in g.v])
                g.teinte = None
                griffes.append(g)
            gm = assembler([g.peint(CHARBON) for g in griffes])
            a.piece("griffes_" + suffixe, gm, None, poil=False)

    # ----- l'armure : les écailles en tuiles, de la nuque à la croupe, sur le haut de la tête et tout le long de la queue -----
    a.piece("ecailles_corps", armure(a, "corps", fil_c, prof_c, 0.03, 0.97, math.radians(122), 13), None, poil=False)
    a.piece("ecailles_tete", armure(a, "tete", fil_t, prof_t, 0.04, 0.44, math.radians(64), 5, vers_queue=-1.0, plus=1.20), None, poil=False)
    a.piece("ecailles_queue", armure(a, "queue", fil_q, prof_q, 0.10, 0.97, math.radians(126), 7, plus=1.16), None, poil=False)
    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("pangolin", styles.style_de("pangolin"), sys.modules[__name__]), "Pangolin")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py pangolin). Pivots : haut des pattes, nuque, racine de la queue ; les gestes sont réglés
# sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.270                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.000, 0.415)),
    ('tete', 'corps', (0.000, -0.290, 0.400)),
    ('queue', 'corps', (0.000, 0.260, 0.340)),
    ('patte_av_G', 'corps', (0.130, -0.165, 0.270)),
    ('patte_ar_G', 'corps', (0.135, 0.100, 0.270)),
]

PORTEURS = [
    ('oeil_reflet', 'tete'), ('ecailles_tete', 'tete'), ('ecailles_queue', 'queue'), ('ecailles_corps', 'corps'),
    ('griffes_av', 'patte_av', True), ('griffes_ar', 'patte_ar', True),
    ('patte_av', 'patte_av', True), ('patte_ar', 'patte_ar', True), ('corps', 'corps'), ('queue', 'queue'),
    ('tete', 'tete'), ('oeil', 'tete'), ('nez', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'),
    ('cil_0', 'paupiere_0'), ('cil_1', 'paupiere_1'),
]


def repos(t):
    """Il respire, renifle d'un côté puis de l'autre, la queue balaie un peu le sol, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(4 * g - 3 * d + 2 * max(0.0, onde(t, 8)), -4 * g + 3 * d, 14 * g - 12 * d))
    p.add('queue', rot=(0, 0, 8 * onde(t, 1)))
    p.ouvert = borne(1 - 0.3 * g - cloche(t, 0.08, 0.02) - cloche(t, 0.62, 0.02))
    return p


def avance(t):
    """Sa marche : les pattes alternent, le corps se dandine, la tête dodeline, la queue traîne en balançant."""
    p = Pose()
    c, s = math.cos(math.tau * t), math.sin(math.tau * t)
    pas = 24.0
    creux = JAMBE * (1 - math.cos(math.radians(pas * s))) * 0.5
    p.add('corps', pos=(0, 0, -creux), rot=(1.0 * onde(t, 2, 0.1), 3 * c, 2.5 * s))
    for nom, sens in [('patte_av_G', 1), ('patte_ar_D', 1), ('patte_av_D', -1), ('patte_ar_G', -1)]:
        p.add(nom, rot=(pas * sens * s, 0, 0), pos=(0, 0, 0.03 * max(0.0, -sens * c)))
    p.add('tete', rot=(-3 + 2 * onde(t, 2, -0.1), 0, -2 * s))
    p.add('queue', rot=(-4, 0, -9 * s))
    return p


def mange(t):
    """Il baisse le museau vers le sol, lape des fourmis à petits coups, puis relève la tête."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(30 * bas + 6 * coups + 3 * leve * onde(t, 12), -3 * leve, 10 * leve))
    p.add('queue', rot=(0, 0, -6 * onde(t, 2)))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, sautille, retombe, et fête ça d'un coup de queue."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.050 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-20 * vol, 0, 0))
    p.paire('patte_ar', rot=(16 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    p.add('queue', rot=(-10 * vol, 0, 18 * fouet))
    return p


def dort(t):
    """Il se roule à moitié en boule : la tête rentrée sous lui, la queue ramenée, les yeux fermés, il respire lentement."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.120), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-60, 0, 12))
    p.paire('patte_ar', rot=(58, 0, 10))
    p.add('tete', rot=(40, 4, 30))
    p.add('queue', rot=(10, 0, 50))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
