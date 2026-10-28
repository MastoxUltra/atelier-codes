# Faunimo : l'ouvrier Colab (session Puissance, 27/10). Une 3e carte pour les photos Godot, à côté des deux de Kaggle.
#
# Arthur, une seule fois : dans Colab, la clé « Secrets » (à gauche), ajouter KAGGLE_USERNAME (masrox) et KAGGLE_KEY
# (la « key » de kaggle.json, créé sur kaggle.com/settings > Create New Token), « Accès au carnet » coché.
# Puis : Exécution > Modifier le type d'exécution > GPU T4, et Exécution > Tout exécuter. L'onglet reste ouvert.
#
# Le carnet tire le jeu (masrox/faunimo-jeu) une fois, puis attend les lots que le PC dépose dans masrox/faunimo-colab-lot
# (atelier_colab.py) ; chaque lot passe par le même carnet.py que Kaggle, et sa sortie repart dans masrox/faunimo-colab-sortie.
# Aucune clé n'est écrite ni affichée : elle ne vit que dans les variables d'environnement de cette séance.
#
# (27/10) Saturn Cloud, le même fichier : le secret KAGGLE_API_TOKEN attaché au Jupyter Server en variable d'environnement,
# puis dans un terminal : curl -sLO https://raw.githubusercontent.com/MastoxUltra/atelier-codes/main/colab/ouvrier.py
# && nohup python ouvrier.py > ouvrier.log 2>&1 &   (canal masrox/faunimo-saturn-lot, à part de Colab)
import glob
import json
import os
import shutil
import subprocess
import time
import zipfile

try:                                                   # (27/10) le même ouvrier sur Saturn Cloud : secrets en variables d'environnement
    from google.colab import userdata
    OUVRIER = "colab"
except ImportError:
    userdata = None
    OUVRIER = os.environ.get("FAUNIMO_OUVRIER", "saturn")


def secret(nom):
    if userdata is None:
        return os.environ.get(nom)
    try:
        return userdata.get(nom)
    except Exception:                                  # secret absent, ou accès au carnet non coché
        return None


# (27/10) le jeton du NOUVEAU type (KGAT_…, page « API Tokens ») va dans KAGGLE_API_TOKEN ; l'ancienne clé dans KAGGLE_KEY
os.environ["KAGGLE_USERNAME"] = secret("KAGGLE_USERNAME") or "masrox"
jeton, cle = secret("KAGGLE_API_TOKEN"), secret("KAGGLE_KEY")
if jeton:
    os.environ["KAGGLE_API_TOKEN"] = jeton
elif cle and cle.startswith("KGAT_"):
    os.environ["KAGGLE_API_TOKEN"] = cle
elif cle:
    os.environ["KAGGLE_KEY"] = cle
else:
    raise SystemExit("Secret KAGGLE_API_TOKEN ou KAGGLE_KEY introuvable (la clé 🔑 à gauche, « Accès au carnet » coché)")
print("jeton Kaggle :", "nouveau type" if "KAGGLE_API_TOKEN" in os.environ else "ancienne clé", "(jamais affiché)")
subprocess.run(["pip", "install", "-q", "-U", "kaggle>=2.2"], check=True)     # les jetons KGAT_ : kaggle 2.x
if not shutil.which("nvidia-smi"):                     # les lots sont des photos sur carte : sans carte, rien à faire ici
    raise SystemExit("Pas de carte graphique sur cette machine : choisir une machine avec GPU (T4), puis relancer")
print(subprocess.run(["nvidia-smi", "--query-gpu=name,driver_version", "--format=csv,noheader"], capture_output=True, text=True).stdout)

LOT, SORTIE, JEU = "masrox/faunimo-%s-lot" % OUVRIER, "masrox/faunimo-%s-sortie" % OUVRIER, "masrox/faunimo-jeu"
# Colab : /content et /donnees ; ailleurs on n'est pas root : le dossier personnel, et /donnees par sudo s'il le permet
BASE = "/content" if OUVRIER == "colab" else os.path.expanduser("~/faunimo")
if OUVRIER != "colab" and not os.path.isdir("/donnees"):
    subprocess.run("sudo -n mkdir -p /donnees && sudo -n chown $(id -u) /donnees", shell=True)
DONNEES = "/donnees" if os.access("/donnees", os.W_OK) or OUVRIER == "colab" else BASE + "/donnees"
print("ouvrier :", OUVRIER, "| lots :", LOT, "| données :", DONNEES, flush=True)


def k(*args, delai=3600):
    r = subprocess.run(["kaggle"] + list(args), capture_output=True, text=True, timeout=delai)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def deplier(dossier):
    """Kaggle rend les dossiers en .zip (dir-mode zip) : on les déplie sur place, jusqu'au bout."""
    while True:
        zips = glob.glob(dossier + "/**/*.zip", recursive=True)
        if not zips:
            return
        for z in zips:
            cible = os.path.splitext(z)[0]                 # faunimo.zip -> faunimo/, faunimo-jeu.zip -> faunimo-jeu/
            with zipfile.ZipFile(z) as f:
                f.extractall(cible)
            os.remove(z)
            seul = os.listdir(cible)                       # le zip contenait déjà son dossier : faunimo/faunimo -> faunimo
            if len(seul) == 1 and seul[0] == os.path.basename(cible) and os.path.isdir(os.path.join(cible, seul[0])):
                tmp = cible + "-tmp"
                os.rename(os.path.join(cible, seul[0]), tmp)
                os.rmdir(cible)
                os.rename(tmp, cible)


# 1. le jeu, une fois par séance (environ 8 Go)
if not glob.glob(DONNEES + "/faunimo-jeu/art/modeles"):
    os.makedirs(BASE + "/jeu", exist_ok=True)
    print("jeu :", k("datasets", "download", "-d", JEU, "-p", BASE + "/jeu", "--unzip")[1][-300:])
    deplier(BASE + "/jeu")
    trouve = [os.path.dirname(os.path.dirname(p)) for p in glob.glob(BASE + "/jeu/**/art/modeles", recursive=True)]
    os.makedirs(DONNEES, exist_ok=True)
    if trouve and not os.path.exists(DONNEES + "/faunimo-jeu"):
        os.symlink(trouve[0], DONNEES + "/faunimo-jeu")
print("gros fichiers :", os.path.realpath(DONNEES + "/faunimo-jeu"))

# 2. la boucle : un lot à la fois, tant que la séance dure
# (27/10) le lot en tête se lit dans lot.txt (un seul petit fichier) : la liste des fichiers du jeu de données est découpée
# en pages, et lot-<id>.txt n'était jamais sur la première (des milliers de fichiers de faunimo/ passent avant)
def lot_en_tete():
    tete = BASE + "/tete"
    shutil.rmtree(tete, ignore_errors=True)
    os.makedirs(tete)
    k("datasets", "download", "-d", LOT, "-f", "lot.txt", "-p", tete, "--force", delai=300)
    deplier(tete)
    for f in glob.glob(tete + "/**/lot.txt", recursive=True):
        return open(f, encoding="utf-8").read().strip()
    return None


def rendre(lot, dossier, nom_marque, texte):
    """La sortie d'un lot (ou sa seule marque d'erreur) dans le jeu de données de sortie, que le PC surveille."""
    global creee
    envoi = BASE + "/envoi"
    shutil.rmtree(envoi, ignore_errors=True)
    os.makedirs(envoi)
    if dossier and os.path.isdir(dossier):
        shutil.make_archive(os.path.join(envoi, lot), "zip", dossier)
    open(os.path.join(envoi, "%s-%s.txt" % (nom_marque, lot)), "w").write(texte)
    json.dump({"title": "Faunimo %s sortie" % OUVRIER, "id": SORTIE, "licenses": [{"name": "other"}]},
              open(os.path.join(envoi, "dataset-metadata.json"), "w"))
    if creee:
        print(k("datasets", "version", "-p", envoi, "-m", lot, "-q")[1][-200:])
    else:
        print(k("datasets", "create", "-p", envoi, "-q")[1][-200:])
        creee = True


def faire(lot):
    """Un lot : téléchargé (deux essais), passé par le carnet, rendu. Une faute lève RuntimeError : le lot est mis de côté."""
    for essai in (1, 2):
        shutil.rmtree(BASE + "/lot", ignore_errors=True)
        os.makedirs(BASE + "/lot")
        # (28/10) fichier par fichier : le lot tient en trois fichiers (faunimo.paquet), et le téléchargement du jeu de
        # données entier ne rendait rien sur Colab (« ni travaux.json ni carnet.py »)
        for f in ("travaux.json", "carnet.py", "faunimo.paquet"):
            print(f, ":", k("datasets", "download", "-d", LOT, "-f", f, "-p", BASE + "/lot", "--force")[1][-160:], flush=True)
        deplier(BASE + "/lot")
        for f in ("travaux.json", "carnet.py", "faunimo.paquet"):    # un fichier rendu zippé : faunimo.paquet/faunimo.paquet
            dedans = os.path.join(BASE, "lot", f, f)
            if os.path.isfile(dedans):
                os.rename(dedans, os.path.join(BASE, "lot", f + ".tmp"))
                shutil.rmtree(os.path.join(BASE, "lot", f))
                os.rename(os.path.join(BASE, "lot", f + ".tmp"), os.path.join(BASE, "lot", f))
        travaux = glob.glob(BASE + "/lot/**/travaux.json", recursive=True)
        carnets = glob.glob(BASE + "/lot/**/carnet.py", recursive=True)
        if travaux and carnets:
            break
        print("lot sans travaux.json ni carnet.py (essai %d) :" % essai, os.listdir(BASE + "/lot")[:10], flush=True)
        time.sleep(90)
    else:
        raise RuntimeError("le lot téléchargé n'a ni travaux.json ni carnet.py")
    global import_cherche
    if not import_cherche and not os.path.exists(DONNEES + "/godot-cache.tar"):
        # (27/10) l'import gardé : essai_distant.py le déplie avant l'import. Introuvable (9 Go, Kaggle ne le rend pas
        # toujours) : on ne le redemande plus, Godot importe normalement, et garde son import d'un lot à l'autre ici
        import_cherche = True
        print("import gardé :", k("kernels", "output", "masrox/faunimo-import", "-p", DONNEES, "--file-pattern",
                                  r"godot-cache\.tar", delai=1800)[1][-200:], flush=True)
        if not os.path.exists(DONNEES + "/godot-cache.tar"):
            print("import gardé introuvable : import normal", flush=True)
    sortie = BASE + "/sortie-" + lot
    shutil.rmtree(sortie, ignore_errors=True)
    env = dict(os.environ, BIBELOTS_JEU_GROS=DONNEES + "/faunimo-jeu")
    r = subprocess.run(["python", carnets[0], "--entree", os.path.dirname(travaux[0]), "--sortie", sortie, "--base", BASE + "/base"], env=env)
    print("carnet : code", r.returncode, flush=True)
    rendre(lot, sortie, "fait", time.strftime("%Y-%m-%d %H:%M:%S"))


faits = set()
import_cherche = False
creee = k("datasets", "status", SORTIE)[0] == 0 and "ready" in k("datasets", "status", SORTIE)[1]
vu = 0
while True:
    try:
        lot = lot_en_tete()
    except Exception as e:                             # une panne passagère de Kaggle : on réessaie dans une minute
        print("lot en tête illisible :", repr(e)[:200], flush=True)
        lot = None
    if not lot or lot in faits:
        if time.time() - vu > 600:
            print(time.strftime("%H:%M"), "j'attends un lot", flush=True)
            vu = time.time()
        time.sleep(60)
        continue
    print(time.strftime("%H:%M"), "lot", lot, flush=True)
    faits.add(lot)
    try:
        faire(lot)
    except Exception as e:                             # (27/10) jamais la boucle par terre : le lot est mis de côté
        print("LOT MIS DE CÔTÉ :", lot, ":", repr(e)[:300], flush=True)
        try:
            rendre(lot, None, "erreur", repr(e)[:1000])
        except Exception as e2:
            print("marque d'erreur pas envoyée :", repr(e2)[:200], flush=True)
