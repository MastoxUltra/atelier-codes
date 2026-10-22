"""Le bœuf musqué en peluche de magasin : un brun encre, presque noir, qui disparaît sous sa propre laine : une grande
jupe de poils qui lui tombe jusqu'aux chaussettes crème, la bosse des épaules, une selle crème sur le dos, la tête
basse sous un casque de cornes ivoire (le bouclier du front, puis les cornes qui descendent le long des joues et
remontent à la pointe). Un mur de laine, têtu, qui n'a rien à prouver : il vous regarde par en dessous, sans bouger.

    python boeuf_musque.py        fabrique la fiche art/apercus/animaux/boeuf_musque.png (peluche de magasin, palier 4)
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

# le style B adoucit les couleurs (vers leur gris) : on les donne plus vives que l'effet voulu
ENCRE = M.hexa("#5d463c")                     # la dominante : brun encre (le poil le fonce presque jusqu'au noir : on le prend plus clair)
SOUS = M.hexa("#3a2b26")                      # le dessous de la jupe, les mèches du bas
CREME = M.hexa("#fff0d2")                     # les chaussettes
SELLE = M.hexa("#8f7658")                     # la selle : un beige pâle, comme la référence (crème, elle faisait une tache)
IVOIRE = M.hexa("#cdb894")                    # l'accent : les cornes, un ivoire chaud (la référence : corne claire)
CORNE = M.hexa("#6e5a44")                     # le bout des cornes, les sabots
NEZ = M.hexa("#b9ab98")                       # le museau : pâle, comme le vrai (le visage se lit enfin)
# (16/10, planche 27 : l'auteur veut les proportions d'un vrai modèle) : relevées sur la référence (references_3d/boeuf_musque,
# CC-BY, la (3) importée en pose de repos : mesurée, rien d'importé) : un long corps, la bosse haute sur les épaules, la
# croupe à peine plus basse, la jupe jusqu'à mi-jambe, la tête basse devant les épaules
# (3e essai : « une butte ronde ») : un corps 1,4 fois plus long que haut, la grosse bosse des épaules, le dos qui
# descend vers la croupe, la tête basse devant la bosse
# (18/10, 4e essai : la croupe finissait en pointe, le corps 1,75 fois plus long que haut) : un corps plus court (0,90 m
# pour 0,66 de haut : 1,37), la croupe ronde et franche, la bosse plus haute et plus serrée sur les épaules
CORPS = Vector((0.0, 0.060, 0.360))
TETE = Vector((0.0, -0.470, 0.320))           # grosse et basse : le front aux trois quarts de la bosse, le menton près de la jupe
JUPE_Y = 0.440                                # la demi-longueur du corps là où naît la jupe
LACET, PIQUE = 24.0, -6.0                    # la tête tournée vers nous, le nez baissé


def meche(chemin, large, face, plat=0.36, long_pointe=0.93, cotes=18):
    """Une mèche plate (le geste du cheval et du renne) : un fuseau tourné, aplati, couché le long d'un chemin ;
    « face » : la direction de son épaisseur (on la voit de plat depuis là)."""
    p = A.courbe(chemin, 8)
    fait = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(p, axis=0), axis=1))])
    sens = np.gradient(p, fait, axis=0)
    L = float(fait[-1])
    n0 = np.asarray(face, float)

    def couche(v):
        s = np.clip(v[:, 2], 0.0, L)
        c = np.stack([np.interp(s, fait, p[:, k]) for k in range(3)], axis=-1)
        t = np.stack([np.interp(s, fait, sens[:, k]) for k in range(3)], axis=-1)
        t /= np.linalg.norm(t, axis=1, keepdims=True)
        x = np.cross(n0, t)
        x /= np.maximum(np.linalg.norm(x, axis=1, keepdims=True), 1e-9)
        return c + t * (v[:, 2] - s)[:, None] + v[:, 0:1] * x + v[:, 1:2] * np.cross(t, x)
    prof = A.profil([(0, 0), (0.60 * large, 0.05 * L), (0.95 * large, 0.22 * L), (large, 0.42 * L), (0.72 * large, 0.70 * L),
                     (0.30 * large, long_pointe * L), (0.06 * large, 0.985 * L), (0, L)], 5)
    return A.tour(prof, cotes).etire(1.0, plat, 1.0).sculpte(couche)


def construire():
    a = K.Animal("boeuf_musque")
    a.taille = 2.40

    # ----- le corps : une masse ronde, la bosse haute sur les épaules, la croupe basse -----
    def masse(v):
        w = v.copy()
        r = np.hypot(w[:, 1], w[:, 2])                                 # vu de côté, un pain (la référence) : la croupe ronde
        uy = np.where(r > 1e-9, w[:, 1] / np.maximum(r, 1e-9), 0.0)    # mais haute et franche, pas une pointe
        uz = np.where(r > 1e-9, w[:, 2] / np.maximum(r, 1e-9), 0.0)
        e = 0.85 - 0.15 * K.lisse((uy + 0.2) / 0.6)
        w[:, 1] = r * np.sign(uy) * np.abs(uy) ** e
        w[:, 2] = r * np.sign(uz) * np.abs(uz) ** e
        w = K.bosse(w, (0, -0.40, 0.92), 0.85, 0.20)                   # la grosse bosse des épaules, haute (5e essai : plus franche)
        s = w * [0.205, 0.450, 0.190]
        s[:, 2] *= 1 - 0.06 * K.lisse((w[:, 1] + 0.1) / 1.1) * K.lisse((w[:, 2] + 0.3) / 0.6)   # le dos qui descend vers la croupe
        return s
    a.piece("corps", A.boule(1.0, 56, 28).sculpte(masse), ENCRE, pos=CORPS)
    # la selle crème : un large pan sur le dos, derrière la bosse
    a.rustine("selle", "corps", CORPS + Vector((0, 0.00, 0.0)), (0, 0.25, 1.0), lambda th: 0.46 - 0.10 * math.cos(2 * th), SELLE, 0.004, 0)

    # ----- la jupe de poils : une trentaine de longues mèches plates, nées du flanc, qui tombent en s'évasant jusqu'à
    #       mi-jambe, une sur deux plus sombre (le geste des fanons du cheval) -----
    rng = np.random.default_rng(7)
    claires, sombres = None, None
    for i in range(36):
        t = 2 * math.pi * (i + rng.uniform(-0.25, 0.25)) / 36
        base = np.array([0.196 * math.cos(t), CORPS.y + JUPE_Y * math.sin(t)])
        radial = np.array([math.cos(t) * 1.0, math.sin(t) * 0.62])
        radial /= np.linalg.norm(radial)
        k = 0.85 + 0.40 * rng.random() + 0.18 * max(0.0, -math.sin(t))                # plus longues devant, là où il est plus laineux
        z0 = CORPS.z - 0.03
        chemin = [(base[0] * 0.94, base[1] * 0.94 + CORPS.y * 0.06, z0 + 0.04),
                  (base[0] + radial[0] * 0.010, base[1] + radial[1] * 0.010, z0 - 0.07),
                  (base[0] + radial[0] * 0.040, base[1] + radial[1] * 0.040, z0 - 0.115 * k),
                  (base[0] + radial[0] * 0.062, base[1] + radial[1] * 0.062, z0 - 0.165 * k)]   # à mi-jambe : les chaussettes se voient
        m = meche(chemin, 0.054 + 0.010 * rng.random(), (radial[0], radial[1], 0.0), 0.40)
        if i % 2:
            sombres = m if sombres is None else sombres + m
        else:
            claires = m if claires is None else claires + m
    a.piece("meches_a", claires, ENCRE)
    a.piece("meches_b", sombres, SOUS)

    # ----- les chaussettes crème : quatre jambes courtes qui dépassent de la jupe, les sabots corne -----
    for nom, x, y in (("av_G", 0.110, -0.240), ("av_D", -0.110, -0.240), ("ar_G", 0.115, 0.360), ("ar_D", -0.115, 0.360)):
        # (18/10) : le haut de la jambe brun sous la jupe (crème, il se voyait par les fentes des mèches comme des taches)
        a.piece("jambe_" + nom, K.tube_peint(A.courbe([(x, y, 0.300), (x, y - 0.004, 0.150), (x, y - 0.010, 0.040)], 5), 0.058,
                                             [(0.50, SOUS), (1.0, CREME)], 16), None)
        a.piece("sabot_" + nom, A.boule(1.0, 24, 12).etire(0.056, 0.066, 0.036), CORNE, pos=(x, y - 0.014, 0.026), poil=False)

    # ----- la tête : longue, lourde, penchée ; le museau pâle bien en vue, des poils longs sur les joues -----
    H = A.repere(TETE, (PIQUE, 0, LACET))
    H3 = H.to_3x3()

    def tete_f(v):
        s = v.copy()
        rh = np.hypot(s[:, 0], s[:, 1])                            # (18/10) un visage plus large et plus plat devant : les
        ux = np.where(rh > 1e-9, s[:, 0] / np.maximum(rh, 1e-9), 0.0)   # deux yeux y tiennent, ronds, sans sortir du profil
        uy = np.where(rh > 1e-9, s[:, 1] / np.maximum(rh, 1e-9), 0.0)
        p = 1.0 - 0.50 * K.lisse(-uy / 0.6)
        s[:, 0] = rh * np.sign(ux) * np.abs(ux) ** p
        s[:, 1] = rh * np.sign(uy) * np.abs(uy) ** p
        s[:, 0] *= 0.78 + 0.10 * K.lisse((-v[:, 1] + 0.1) / 0.9)
        s = K.bosse(s, (0, -1, -0.2), 0.12, 0.35)
        return s * [0.172, 0.200, 0.150]
    a.piece("tete", A.boule(1.0, 48, 24).sculpte(tete_f), SOUS, mat=H)
    # (3e essai : le nez faisait une carotte) : un museau large, plat et clair, deux narines sombres devant, sans cône
    museau = A.boule(1.0, 36, 18).sculpte(lambda v: K.emousse(v, 0.62)).etire(0.088, 0.070, 0.056)
    a.piece("museau", museau, NEZ, mat=H @ A.repere((0, -0.175, -0.055)))
    for nom_n, c in (("G", 1), ("D", -1)):
        pn, nn = a.surface("museau", H @ Vector((0, -0.175, -0.055)), H.to_3x3() @ Vector((c * 0.40, -0.90, 0.10)))
        a.piece("narine_" + nom_n, A.boule(1.0, 14, 7).etire(0.011, 0.016, 0.005), M.hexa("#2a2220"),
                mat=A.cadre(pn + nn * 0.001, nn, H.to_3x3() @ Vector((c * 0.30, 0.0, 1.0))), poil=False)
    a.tete = H @ Vector((0, -0.200, -0.040))
    a.fusion_a_part = ("narine",)                                  # posées sur la peau gonflée, pas fondues

    # ----- les yeux : ronds et vivants, au regard calme, sous la corne (plus de paupière lourde) -----
    # (18/10, Cohérence : de face, un œil à moitié caché par la corne) : sur le devant du visage, au-dessus du museau, et
    # tournés vers l'avant (la normale de la joue, mêlée à l'avant de la tête) : entiers de face et de trois quarts
    # (18/10, 5e essai : tournés vers l'avant plus que la joue, ils sortaient du profil comme des disques) : à plat sur
    # la joue (seulement redressés un peu, pour ne pas regarder le ciel), plus petits
    # (6e essai : sur la joue, ils restaient au bord du profil) : sur le visage plat, plus près du milieu, au-dessus du
    # museau ; leur normale n'ouvre que de 11° vers dehors : entiers de face comme des deux trois quarts
    for nom, c in (("G", 1), ("D", -1)):
        p, n = a.surface("tete", H.to_translation(), H3 @ Vector((c * 0.30, -0.90, 0.24)))
        nl = H3.inverted() @ n
        vers = H3 @ Vector((nl.x, nl.y, 0.5 * nl.z)).normalized()
        a.oeil("oeil_" + nom, p + n * 0.006, vers, 0.0300)

    # ----- le casque de cornes : le bouclier ivoire sur le front, puis la corne qui descend le long de la joue et
    #       remonte, la pointe corne tournée vers l'avant -----
    # (18/10, 7e essai : fondu dans la peau comme une feutrine, son bord se froissait en papier sur la racine des cornes) :
    # « casque » : une pièce dure, posée sur la peau et lisse, un peu plus large et plus épaisse pour couvrir les racines
    a.piece("casque", A.boule(1.0, 40, 18).etire(0.135, 0.088, 0.040), IVOIRE, mat=H @ A.repere((0, -0.040, 0.134), (-10, 0, 0)), poil=False)   # plus haut : le poil ne le traverse pas
    for nom, c in (("G", 1), ("D", -1)):
        # (2e essai : de grands arcs blancs) : les cornes de la référence, couleur de corne, qui collent aux joues
        # (18/10) : posées SUR la joue (chaque point visé sur la tête, puis écarté de son rayon : rien qui flotte), la
        # descente derrière l'œil, le crochet sur le côté, la pointe qui remonte en dehors de l'œil
        # (18/10, 5e essai : collées à 0,75 rayon, le poil les avalait) : posées sur le poil, plus épaisses, et le crochet
        # qui s'écarte de la joue, la pointe brune qui remonte bien en vue
        # (6e essai : une bande épaisse collée tout du long faisait un casque audio) : fines comme sur la référence, la
        # descente seule contre la joue, puis le crochet qui SORT vers dehors et remonte, la pointe brune bien à l'écart
        rayon_c = lambda t: 0.004 + 0.022 * (1 - t) ** 0.8
        chemin = [H @ Vector((c * 0.060, -0.030, 0.130))]                    # la racine, sous le bouclier
        for i_, (x_, y_, z_, sort) in enumerate(((c * 0.140, -0.020, 0.110, 0.002), (c * 0.190, 0.000, 0.020, 0.004),
                                                 (c * 0.170, -0.030, -0.080, 0.006))):
            pc, nc = a.surface("tete", H.to_translation(), H3 @ Vector((x_, y_, z_)))
            chemin.append(pc + nc * (0.8 * rayon_c(0.2 * (i_ + 1)) + sort))
        chemin.append(chemin[-1] + H3 @ Vector((c * 0.050, -0.020, 0.005)))     # le crochet sort de la joue
        chemin.append(chemin[-1] + H3 @ Vector((c * 0.022, -0.018, 0.050)))     # la pointe remonte
        corne = K.tube_peint(A.courbe(chemin, 6), rayon_c, [(0.55, IVOIRE), (1, CORNE)], 18)   # la pointe fine (coupée net, elle faisait tube : 16/10)
        a.piece("corne_" + nom, corne, None, poil=False)

    return a


if __name__ == "__main__":
    import styles
    K.planche(lambda: styles.construire("boeuf_musque", styles.style_de("boeuf_musque"), sys.modules[__name__]), "Bœuf musqué")


# ---------------------------------------------------------------- pour le jeu : son squelette et ses animations
# (voir usine.py : python usine.py boeuf_musque). Généré d'après la géométrie du modèle (pivots : haut des pattes, base des
# oreilles, nuque, racine de la queue) ; les gestes sont réglés sur la longueur de ses pattes. Mesures avant a.taille.

from poses import Pose, borne, cloche, onde

JAMBE = 0.294                                        # de l'épaule (ou de la hanche) au sol

OS = [
    ('racine', None, (0, 0, 0)),
    ('corps', 'racine', (0.000, 0.235, 0.335)),
    ('tete', 'corps', (-0.042, -0.268, 0.321)),
    ('patte_av_G', 'corps', (0.120, -0.261, 0.294)),
    ('patte_ar_G', 'corps', (0.130, 0.309, 0.294)),
]

PORTEURS = [
    ('meches_a', 'corps'), ('jambe_av', 'patte_av', True), ('jambe_ar', 'patte_ar', True), ('meches_b', 'corps'),
    ('sabot_av', 'patte_av', True), ('sabot_ar', 'patte_ar', True), ('casque', 'tete'), ('lourde', 'tete'),
    ('museau', 'tete'), ('narine', 'tete'), ('corps', 'corps'), ('selle', 'corps'), ('corne', 'tete'), ('tete', 'tete'), ('oeil', 'tete'),
    ('nez', 'tete'), ('paupiere_0', 'paupiere_0'), ('paupiere_1', 'paupiere_1'), ('cil_0', 'paupiere_0'),
    ('cil_1', 'paupiere_1'),
]

def repos(t):
    """Il respire, tourne la tête d'un côté puis de l'autre, une oreille bouge, un clignement."""
    p = Pose()
    r = onde(t, 2)
    g, d = cloche(t, 0.28, 0.16), cloche(t, 0.72, 0.13)
    p.add('corps', ech=(1 + 0.010 * r, 1, 1 + 0.018 * r))
    p.add('tete', rot=(3 * g - 2 * d, -4 * g + 3 * d, 16 * g - 12 * d))
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
    return p


def mange(t):
    """Il baisse la tête vers le sol, quelques bouchées, puis la relève et mâche."""
    p = Pose()
    leve = cloche(t, 0.84, 0.15)
    bas = 1 - leve
    coups = max(0.0, onde(t, 4)) ** 2 * bas
    p.add('corps', rot=(5 * bas, 0, 0))
    p.add('tete', rot=(40 * bas + 8 * coups + 3 * leve * onde(t, 12), -3 * leve, 12 * leve))
    p.ouvert = borne(1 - cloche(t, 0.70, 0.03))
    return p


def joie(t):
    """Il se tasse, bondit, retombe, et fête ça : les oreilles, la queue, les ailes."""
    p = Pose()
    tasse = cloche(t, 0.12, 0.12, False)
    vol = math.sin(math.pi * borne((t - 0.18) / 0.42))
    salut = cloche(t, 0.72, 0.16, False)
    fouet = onde(t, 6) * cloche(t, 0.80, 0.18, False)
    p.add('corps', pos=(0, 0, -0.03 * tasse + 0.088 * vol), rot=(8 * tasse - 10 * vol + 8 * salut, 0, 0))
    p.paire('patte_av', rot=(-22 * vol, 0, 0))
    p.paire('patte_ar', rot=(18 * vol, 0, 0))
    p.add('tete', rot=(-8 * vol + 8 * tasse, 0, 0))
    return p


def dort(t):
    """Il s'affaisse, la tête repose de côté, les yeux fermés, une respiration lente."""
    p = Pose()
    r = onde(t, 1)
    p.ouvert = 0.0
    p.add('corps', pos=(0, 0, -0.162), ech=(1 + 0.012 * r, 1, 1 + 0.024 * r))
    p.paire('patte_av', rot=(-68, 0, 14))
    p.paire('patte_ar', rot=(66, 0, 10))
    p.add('tete', rot=(32, 4, 40))
    return p


ANIMATIONS = {"repos": (120, repos, True), "avance": (24, avance, True), "mange": (60, mange, True),
              "joie": (48, joie, False), "dort": (120, dort, True)}
