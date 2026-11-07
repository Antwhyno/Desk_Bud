"""MicroPython / ESP32-C3 / OLED SH1106 128x64 en I2C (SDA=GPIO8, SCL=GPIO9)

Tout est NON BLOQUANT : une seule boucle, chaque module fait un petit pas.

Fichier requi sur la carte : sh1106.py (pilote SH1106 compatible)"""

import machine
import time
import math
import sys
import random
import sh1106
import gc

#  CONFIGURATION

LARGEUR = 128
HAUTEUR = 64
PIN_SDA = 8
PIN_SCL = 9
ADRESSE_I2C = 0x3C
FREQ_I2C = 100000

PERIODE_IMAGE_MS = 30       # ~40 img/s maximum (si le pilote suit)
HUMEUR_AUTO = True          # petites expressions spontanees (joyeuse, curieuse)

# --- Reseau (laisser WIFI_SSID vide = reseau completement desactive) ---------
WIFI_SSID = "Yoyomah_EXT"
#"LY-SI2-23 2983" "math" # Le réseau d'un pc fonctionne uniquement si la Bande réseau est configurée sur 2.4 GHz
WIFI_MOT_DE_PASSE = "famille_bob_3381"
#"12345678" #"papillon"
FUSEAU_FRANCE = True        # heure d'ete / hiver automatique
METEO_URL = ("https://api.open-meteo.com/v1/forecast?latitude=47.3319"
             "&longitude=5.0322&current=temperature_2m&timezone=auto")
METEO_PERIODE_S = 300       # Actualisé toutes les 5 minutes
NTP_PERIODE_S = 6 * 3600

# --- Boutons : {"nom": numero_GPIO}  (vide = aucun bouton) -------------------
# Exemple : BOUTONS = {"expression": 4, "minuteur": 5}
# Chaque bouton relie le GPIO a GND (pull-up interne activee).
BOUTONS = {"expression": 4, "minuteur": 3}  # GPIO4 et GPIO3, boutons vers GND

# --- Liaison PC par USB (texte). ATTENTION : a laisser False sous Thonny, ----
# car Thonny utilise le meme canal serie. A activer pour un usage autonome.
LIAISON_PC_ACTIVE = False


#  OUTILS GENERAUX

ticks_ms = time.ticks_ms
ticks_diff = time.ticks_diff
ticks_add = time.ticks_add


def alea():
    """Nombre aleatoire dans [0, 1[ (getrandbits existe toujours)."""
    return random.getrandbits(16) / 65536.0


def entre(a, b):
    return a + (b - a) * alea()


def entier(a, b):
    """Entier aleatoire dans [a, b] inclus."""
    return a + int(alea() * (b - a + 1))


def signe():
    return 1 if alea() < 0.5 else -1


def borner(v, bas, haut):
    if v < bas:
        return bas
    if v > haut:
        return haut
    return v


def arr(v):
    """Arrondi a l'entier le plus proche (symetrique)."""
    return int(v + 0.5) if v >= 0 else -int(-v + 0.5)


def doux(p):
    """Interpolation cosinus : 0 -> 1 avec depart et arrivee en douceur."""
    return (1.0 - math.cos(math.pi * p)) / 2.0



#  PRIMITIVES GRAPHIQUES (toutes protegees contre les debordements)

def rect_plein(d, x, y, w, h, c):
    if x < 0:
        w += x
        x = 0
    if y < 0:
        h += y
        y = 0
    if x + w > LARGEUR:
        w = LARGEUR - x
    if y + h > HAUTEUR:
        h = HAUTEUR - y
    if w > 0 and h > 0:
        d.fill_rect(x, y, w, h, c)


def disque(d, cx, cy, r, c):
    for dy in range(-r, r + 1):
        dx = int(math.sqrt(r * r - dy * dy) + 0.5)
        rect_plein(d, cx - dx, cy + dy, 2 * dx + 1, 1, c)


def rect_arrondi(d, x, y, w, h, r, c):
    if w <= 0 or h <= 0:
        return
    r = min(r, w // 2, h // 2)
    for i in range(r):
        dy = r - i - 0.5
        retrait = r - int(math.sqrt(max(0.0, r * r - dy * dy)) + 0.5)
        rect_plein(d, x + retrait, y + i, w - 2 * retrait, 1, c)
        rect_plein(d, x + retrait, y + h - 1 - i, w - 2 * retrait, 1, c)
    rect_plein(d, x, y + r, w, h - 2 * r, c)


#  EXPRESSIONS
#  Chaque expression est un tuple de parametres. Le visage glisse en douceur
#  de l'expression courante vers la nouvelle (pas de changement brusque).
#
#  W    largeur de l'oeil          H    hauteur de l'oeil
#  R    rayon des coins            HAUT paupiere haute (px couverts)
#  INCL inclinaison paupiere haute (>0 colere, <0 tristesse)
#  BAS  paupiere basse "joue" (px)  BL   largeur de la bouche (0 = aucune)
#  BC   courbure bouche (>0 sourire, <0 moue)   BO  rayon bouche ouverte
#  DIF  difference de hauteur entre les deux yeux (asymetrie)
#  REG  amplitude des mouvements du regard (0 = regard fixe)
#  CLI  frequence des clignements (0 = jamais)

W, H, R, HAUT, INCL, BAS, BL, BC, BO, DIF, REG, CLI = range(12)

EXPRESSIONS = {
    #            W   H   R  HAUT INCL BAS  BL  BC   BO  DIF  REG  CLI
    "neutre":   (34, 36, 10,  0,   0.0,  0,  0,  0.0, 0,  0.0, 1.0, 1.0),
    "joyeuse":  (34, 30, 12,  0,   0.0, 13, 22,  4.0, 0,  0.0, 0.8, 0.7),
    "fatiguee": (34, 34, 10, 13,   0.0,  0,  0,  0.0, 0,  0.0, 0.6, 1.5),
    "surprise": (36, 42, 14,  0,   0.0,  0, 10,  0.0, 3,  0.0, 0.4, 0.3),
    "triste":   (34, 36, 10,  5,  -10.0, 0, 14, -3.0, 0,  0.0, 0.5, 0.7),
    "curieuse": (34, 34, 10,  0,   0.0,  0,  0,  0.0, 0,  7.0, 1.3, 1.0),
    "endormie": (34, 36, 10, 29,   0.0,  0,  0,  0.0, 0,  0.0, 0.0, 0.0),
}
ORDRE_EXPRESSIONS = ("neutre", "joyeuse", "fatiguee", "surprise",
                     "triste", "curieuse", "endormie")


class Expression:
    def __init__(self):
        self.base = "neutre"          # expression "permanente"
        self.nom = "neutre"           # expression affichee (peut etre temporaire)
        self.cible = EXPRESSIONS["neutre"]
        self.val = [float(v) for v in EXPRESSIONS["neutre"]]
        self.retour_t = None          # fin de l'expression temporaire
        self.prochaine_humeur = ticks_add(ticks_ms(), 20000)


EXPR = Expression()


def definir_expression(nom, duree_ms=0):
    """duree_ms = 0 : expression permanente. Sinon temporaire, puis retour."""
    if nom not in EXPRESSIONS:
        return False
    EXPR.cible = EXPRESSIONS[nom]
    EXPR.nom = nom
    if duree_ms > 0:
        EXPR.retour_t = ticks_add(ticks_ms(), duree_ms)
    else:
        EXPR.base = nom
        EXPR.retour_t = None
    return True


def animer_expression():
    v = EXPR.val
    c = EXPR.cible
    for i in range(12):
        ecart = c[i] - v[i]
        if abs(ecart) < 0.02:
            v[i] = float(c[i])
        else:
            v[i] += ecart * 0.2


def humeur(t):
    """Retour d'expression temporaire + petites humeurs spontanees."""
    if EXPR.retour_t is not None:
        if ticks_diff(t, EXPR.retour_t) >= 0:
            definir_expression(EXPR.base)
            EXPR.prochaine_humeur = ticks_add(t, entier(15000, 45000))
    elif (HUMEUR_AUTO and EXPR.base == "neutre"
          and ticks_diff(t, EXPR.prochaine_humeur) >= 0):
        nom = "joyeuse" if alea() < 0.6 else "curieuse"
        definir_expression(nom, entier(1800, 3500))



#  REGARD : mouvements fluides, pauses, micro-ajustements

GAIN_X = 8      # deplacement horizontal maximal (px)
GAIN_Y = 4      # deplacement vertical maximal (px)


class Regard:
    def __init__(self):
        self.x = 0.0            # position courante normalisee [-1, 1]
        self.y = 0.0
        self.x0 = 0.0
        self.y0 = 0.0
        self.cx = 0.0           # cible
        self.cy = 0.0
        self.debut = 0
        self.duree = 1
        self.en_cours = False
        self.type = 0           # 0 normal, 1 grand, 2 micro-ajustement
        self.micro_suivant = False
        self.prochain = ticks_add(ticks_ms(), 500)


REGARD = Regard()


def _pause_regard():
    r = alea()
    if r < 0.12:
        return entier(180, 400)         # regard vif
    if r < 0.85:
        return entier(350, 1400)        # pause normale
    return entier(2200, 4200)           # long regard fixe


def _choisir_cible(g):
    r = alea()
    if r < 0.25:
        amp = entre(0.10, 0.35)         # faible amplitude
    elif r < 0.65:
        amp = entre(0.40, 0.75)
    else:
        amp = entre(0.80, 1.00)         # prononce
    k = alea()
    if k < 0.40:                        # horizontal
        cx = signe() * amp
        cy = entre(-0.15, 0.15)
    elif k < 0.60:                      # vertical
        cx = entre(-0.15, 0.15)
        cy = signe() * amp
    else:                               # diagonal
        cx = signe() * amp
        cy = signe() * amp * entre(0.6, 1.0)
    if abs(cx - g.x) + abs(cy - g.y) < 0.15:    # evite un "non-mouvement"
        cx = -cx
    return borner(cx, -1.0, 1.0), borner(cy, -1.0, 1.0)


def _lancer_mouvement(g, t, cx, cy, type_):
    g.x0 = g.x
    g.y0 = g.y
    g.cx = cx
    g.cy = cy
    dist = math.sqrt((cx - g.x) ** 2 + (cy - g.y) ** 2)
    if type_ == 2:
        g.duree = entier(70, 120)
    else:
        g.duree = int((90 + 140 * dist) * entre(0.85, 1.2))
    g.debut = t
    g.en_cours = True
    g.type = type_


def mouvement_regard(g, t):
    """Un pas de l'animation du regard (jamais bloquant)."""
    if g.en_cours:
        p = ticks_diff(t, g.debut) / g.duree
        if p >= 1.0:
            g.x = g.cx
            g.y = g.cy
            g.en_cours = False
            if g.type == 1 and alea() < 0.55:
                g.micro_suivant = True              # petit ajustement apres un grand mouvement
                g.prochain = ticks_add(t, entier(90, 260))
            else:
                g.prochain = ticks_add(t, _pause_regard())
        else:
            u = doux(p)
            g.x = g.x0 + (g.cx - g.x0) * u
            g.y = g.y0 + (g.cy - g.y0) * u
    elif ticks_diff(t, g.prochain) >= 0:
        if g.micro_suivant:
            g.micro_suivant = False
            cx = borner(g.x + entre(-0.14, 0.14), -1.0, 1.0)
            cy = borner(g.y + entre(-0.12, 0.12), -1.0, 1.0)
            _lancer_mouvement(g, t, cx, cy, 2)
        else:
            cx, cy = _choisir_cible(g)
            dist = math.sqrt((cx - g.x) ** 2 + (cy - g.y) ** 2)
            type_ = 1 if dist > 0.7 else 0
            _lancer_mouvement(g, t, cx, cy, type_)
            if type_ == 1 and alea() < 0.3:         # on cligne souvent en changeant de cible
                demarrer_clignement(CLIGN, t, 1)


# -----------------------------------------------------------------------------
#  CLIGNEMENTS : machine a etats independante du regard
# -----------------------------------------------------------------------------
SEQ_CLIGN = (0.70, 0.35, 0.08, 0.08, 0.40, 0.75)    # facteur de hauteur
PAS_CLIGN_MS = 18


class Clignement:
    def __init__(self):
        self.seq = None
        self.idx = 0
        self.dernier = 0
        self.facteur = 1.0
        self.prochain = ticks_add(ticks_ms(), 2500)


CLIGN = Clignement()


def demarrer_clignement(c, t, n):
    if c.seq is not None:
        return
    seq = ()
    for i in range(n):
        seq = seq + SEQ_CLIGN
        if i < n - 1:
            seq = seq + (1.0,)          # bref instant ouvert entre deux clignements
    c.seq = seq
    c.idx = 0
    c.dernier = t
    c.facteur = seq[0]


def cligner(c, t, freq):
    """Un pas de l'animation des clignements."""
    if c.seq is not None:
        if ticks_diff(t, c.dernier) >= PAS_CLIGN_MS:
            c.dernier = t
            c.idx += 1
            if c.idx >= len(c.seq):
                c.seq = None
                c.facteur = 1.0
                c.prochain = ticks_add(t, int(entier(1800, 4500) / max(freq, 0.1)))
            else:
                c.facteur = c.seq[c.idx]
    elif freq > 0.05:
        if ticks_diff(t, c.prochain) >= 0:
            r = alea()
            n = 3 if r < 0.04 else (2 if r < 0.20 else 1)
            demarrer_clignement(c, t, n)
    else:
        c.prochain = ticks_add(t, 2000)


# -----------------------------------------------------------------------------
#  DESSIN DU VISAGE
# -----------------------------------------------------------------------------
GAP = 30        # demi-ecart entre les centres des yeux
CY0 = 29        # ordonnee du centre des yeux
Y_BOUCHE = 57


def paupiere_haute(d, x, y, w, h, haut, incl, cote):
    """Masque noir sur le haut de l'oeil, eventuellement incline."""
    if abs(incl) < 0.5:
        rect_plein(d, x, y, w, min(h, int(haut)), 0)
        return
    pas = 2
    for i in range(0, w, pas):
        t = (i + pas / 2) / w - 0.5             # -0.5 (gauche) .. +0.5 (droite)
        if cote:                                 # oeil droit : l'interieur est a gauche
            t = -t
        prof = int(haut + incl * t + 0.5)        # t>0 = cote interieur
        if prof > 0:
            rect_plein(d, x + i, y, pas, min(h, prof), 0)


def dessiner_oeil(d, cx, cy, w, h, r, haut, incl, bas, cote):
    cx = borner(cx, w // 2, LARGEUR - w // 2)
    x = cx - w // 2
    y = cy - h // 2
    rect_arrondi(d, x, y, w, h, r, 1)
    if haut >= 1 or abs(incl) >= 1:
        paupiere_haute(d, x, y, w, h, haut, incl, cote)
    if bas >= 1:
        rayon = w // 2 + 6
        disque(d, cx, y + h + rayon - int(bas), rayon, 0)


def dessiner_bouche(d, cx, cy, largeur, courbe, ouv):
    if ouv >= 1:
        disque(d, cx, cy, ouv, 1)
    elif largeur >= 3:
        demi = largeur // 2
        for i in range(-demi, demi + 1):
            yy = cy + arr(courbe * (1.0 - (i * i) / (demi * demi)))
            rect_plein(d, cx + i, yy, 1, 2, 1)


class EtatDessin:
    def __init__(self):
        self.signature = None


DESSIN = EtatDessin()


def dessiner_visage(d, t):
    """Calcule l'image, et ne rafraichit l'ecran QUE si elle a change."""
    v = EXPR.val
    f = CLIGN.facteur
    ech = borner(v[REG], 0.0, 1.3)

    dx = arr(REGARD.x * GAIN_X * ech)
    dy = arr(REGARD.y * GAIN_Y * ech)
    if ech < 0.15:                                  # endormie : respiration lente
        dy += arr(1.5 * math.sin(t / 700.0))

    persp = arr(REGARD.x * 2 * ech)                 # leger effet de perspective
    w = arr(v[W])
    wg = w - persp
    wd = w + persp
    hg = max(2, arr((v[H] + v[DIF]) * f))
    hd = max(2, arr((v[H] - v[DIF]) * f))
    r = arr(v[R])
    haut = v[HAUT] * f
    incl = v[INCL] * f
    bas = v[BAS] * f
    cy = CY0 + dy
    cxg = LARGEUR // 2 - GAP + dx
    cxd = LARGEUR // 2 + GAP + dx

    bl = arr(v[BL])
    bc = v[BC]
    bo = arr(v[BO])
    bx = LARGEUR // 2 + dx // 2
    by = Y_BOUCHE + dy // 2

    sig = (wg, wd, hg, hd, r, arr(haut), arr(incl * 4), arr(bas),
           cxg, cxd, cy, bl, arr(bc * 4), bo, bx, by,
           HORLOGE.texte, METEO.texte, MINUT.texte)
    if sig == DESSIN.signature:
        return
    DESSIN.signature = sig

    d.fill(0)
    dessiner_oeil(d, cxg, cy, wg, hg, r, haut, incl, bas, 0)
    dessiner_oeil(d, cxd, cy, wd, hd, r, haut, incl, bas, 1)
    dessiner_bouche(d, bx, by, bl, bc, bo)
    superposition(d)
    d.show()                                        # un seul show() par image


def superposition(d):
    """Texte d'information par-dessus le visage (heure, meteo, minuteur)."""
    if HORLOGE.texte:
        n = len(HORLOGE.texte) * 8
        rect_plein(d, LARGEUR - n - 1, 0, n + 1, 9, 0)
        d.text(HORLOGE.texte, LARGEUR - n, 0, 1)
    if METEO.texte:
        n = len(METEO.texte) * 8
        rect_plein(d, 0, 0, n + 1, 9, 0)
        d.text(METEO.texte, 0, 0, 1)
    if MINUT.texte:
        n = len(MINUT.texte) * 8
        rect_plein(d, LARGEUR - n - 1, HAUTEUR - 9, n + 1, 9, 0)
        d.text(MINUT.texte, LARGEUR - n, HAUTEUR - 8, 1)


def yeux(d, t):
    """UNE etape d'animation du visage (non bloquante)."""
    animer_expression()
    mouvement_regard(REGARD, t)
    cligner(CLIGN, t, EXPR.val[CLI])
    dessiner_visage(d, t)



#  RESEAU (thread d'arriere-plan : Wi-Fi + NTP + meteo). Desactive par defaut.

class Reseau:
    def __init__(self):
        self.heure_ok = False
        self.temperature = None
        self.maj_ticks = 0


RES = Reseau()


def _http_get(url):
    try:
        import urequests as rq
    except ImportError:
        import requests as rq
    try:
        return rq.get(url, timeout=20)
    except TypeError:                   # firmware sans parametre timeout
        return rq.get(url)


def _lire_meteo():
    r = None
    try:
        gc.collect()
        print("RAM avant HTTPS :", gc.mem_free())
        r = _http_get(METEO_URL)
        if r.status_code != 200:
            raise OSError("HTTP %d" % r.status_code)    # ex : 503 temporaire
        RES.temperature = float(r.json()["current"]["temperature_2m"])
        RES.maj_ticks = ticks_ms()
    finally:
        if r is not None:
            r.close()
            r = None
        gc.collect()
        print("RAM apres HTTPS :", gc.mem_free())


def _tache_reseau():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    sec_ntp = 0
    sec_meteo = 0
    while True:
        try:
            if not wlan.isconnected():
                wlan.connect(WIFI_SSID, WIFI_MOT_DE_PASSE)
                for _ in range(30):
                    if wlan.isconnected():
                        break
                    time.sleep(0.5)
            if wlan.isconnected():
                if sec_ntp <= 0:
                    try:
                        import ntptime
                        ntptime.timeout = 2
                        ntptime.settime()
                        RES.heure_ok = True
                        sec_ntp = NTP_PERIODE_S
                    except Exception as e:
                        print("NTP :", e)
                        sec_ntp = 30
                if sec_meteo <= 0:
                    try:
                        _lire_meteo()
                        sec_meteo = METEO_PERIODE_S
                    except Exception as e:
                        print("Meteo :", e)
                        sec_meteo = 30
            else:
                print("Wi-Fi indisponible, nouvel essai")
                time.sleep(10)
        except Exception as e:
            print("Reseau :", e)
            time.sleep(10)
        time.sleep(1)
        sec_ntp -= 1
        sec_meteo -= 1


def demarrer_reseau():
    if not WIFI_SSID:
        return
    try:
        import _thread
        try:
            pass
        except Exception:
            pass
        _thread.start_new_thread(_tache_reseau, ())
        print("Tache reseau demarree")
    except Exception as e:
        print("Impossible de demarrer le reseau :", e)


# -----------------------------------------------------------------------------
#  HORLOGE (heure francaise avec changement ete/hiver)
# -----------------------------------------------------------------------------
def _dernier_dimanche(an, mois):
    """Epoch (UTC) de 01:00 UTC le dernier dimanche du mois (mars ou octobre)."""
    wd = time.gmtime(time.mktime((an, mois, 31, 1, 0, 0, 0, 0)))[6]   # 0=lundi
    jour = 31 - ((wd + 1) % 7)
    return time.mktime((an, mois, jour, 1, 0, 0, 0, 0))


def heure_france(ts):
    an = time.gmtime(ts)[0]
    ete = _dernier_dimanche(an, 3) <= ts < _dernier_dimanche(an, 10)
    return time.gmtime(ts + (7200 if ete else 3600))


class Horloge:
    def __init__(self):
        self.texte = ""
        self.prochain = 0


HORLOGE = Horloge()


def horloge(t):
    if ticks_diff(t, HORLOGE.prochain) < 0:
        return
    HORLOGE.prochain = ticks_add(t, 1000)
    if not RES.heure_ok:                    # heure non synchronisee : on n'affiche rien
        HORLOGE.texte = ""
        return
    lt = heure_france(time.time()) if FUSEAU_FRANCE else time.localtime()
    HORLOGE.texte = "%02d:%02d" % (lt[3], lt[4])


# -----------------------------------------------------------------------------
#  METEO (affichage seulement : la requete est faite par la tache reseau)
# -----------------------------------------------------------------------------
class Meteo:
    def __init__(self):
        self.texte = ""
        self.prochain = 0


METEO = Meteo()


def meteo(t):
    if ticks_diff(t, METEO.prochain) < 0:
        return
    METEO.prochain = ticks_add(t, 1000)
    if (RES.temperature is not None
            and ticks_diff(t, RES.maj_ticks) < 15 * 60 * 1000):
        METEO.texte = "%dC" % arr(RES.temperature)
    else:
        METEO.texte = ""


# -----------------------------------------------------------------------------
#  MINUTEUR (compte a rebours non bloquant)
# -----------------------------------------------------------------------------
class Minuteur:
    def __init__(self):
        self.actif = False
        self.fin = 0
        self.alarme_fin = None
        self.texte = ""


MINUT = Minuteur()


def lancer_minuteur(secondes):
    MINUT.fin = ticks_add(ticks_ms(), int(secondes) * 1000)
    MINUT.actif = True
    MINUT.alarme_fin = None


def annuler_minuteur():
    MINUT.actif = False
    MINUT.alarme_fin = None
    MINUT.texte = ""


def minuteur(t):
    if MINUT.actif:
        reste = ticks_diff(MINUT.fin, t)
        if reste <= 0:
            MINUT.actif = False
            MINUT.alarme_fin = ticks_add(t, 6000)
            definir_expression("surprise", 6000)
        else:
            s = (reste + 999) // 1000
            if s >= 3600:
                MINUT.texte = "%dh%02d" % (s // 3600, (s % 3600) // 60)
            else:
                MINUT.texte = "%02d:%02d" % (s // 60, s % 60)
    if MINUT.alarme_fin is not None:
        if ticks_diff(t, MINUT.alarme_fin) >= 0:
            MINUT.alarme_fin = None
            MINUT.texte = ""
        else:
            MINUT.texte = "FIN!" if (t // 400) % 2 else ""


# -----------------------------------------------------------------------------
#  BOUTONS (antirebond, extensible via BOUTONS et evenement_bouton)
# -----------------------------------------------------------------------------
BTN = []        # [nom, Pin, dernier_etat, instant_dernier_changement]


def initialiser_boutons():
    for nom in BOUTONS:
        pin = machine.Pin(BOUTONS[nom], machine.Pin.IN, machine.Pin.PULL_UP)
        BTN.append([nom, pin, 1, 0])


def evenement_bouton(nom):
    """Point d'entree des actions : a adapter selon le materiel."""
    if nom == "expression":
        i = (ORDRE_EXPRESSIONS.index(EXPR.base) + 1) % len(ORDRE_EXPRESSIONS)
        definir_expression(ORDRE_EXPRESSIONS[i])
    elif nom == "minuteur":
        if MINUT.actif:
            annuler_minuteur()
        else:
            lancer_minuteur(300)
    else:
        print("Bouton :", nom)


def gestion_boutons(t):
    for b in BTN:
        etat = b[1].value()
        if etat != b[2] and ticks_diff(t, b[3]) > 40:
            b[2] = etat
            b[3] = t
            if etat == 0:
                evenement_bouton(b[0])


# -----------------------------------------------------------------------------
#  LIAISON PC (USB serie, commandes texte). Desactivee par defaut.
#  Commandes :  EXPR joyeuse   |   MINUTEUR 300   |   STOP
# -----------------------------------------------------------------------------
class LiaisonPC:
    def __init__(self):
        self.poll = None
        self.tampon = ""


PC = LiaisonPC()


def initialiser_liaison_pc():
    if not LIAISON_PC_ACTIVE:
        return
    import select
    PC.poll = select.poll()
    PC.poll.register(sys.stdin, select.POLLIN)


def commande_pc(ligne):
    try:
        p = ligne.strip().split(" ")
        cmd = p[0].upper()
        if cmd == "EXPR":
            definir_expression(p[1], 4000)
        elif cmd == "MINUTEUR":
            lancer_minuteur(int(p[1]))
        elif cmd == "STOP":
            annuler_minuteur()
    except Exception as e:
        print("Commande invalide :", e)


def liaison_pc(t):
    if PC.poll is None:
        return
    for _ in range(32):                      # lecture bornee : jamais bloquant
        if not PC.poll.poll(0):
            break
        c = sys.stdin.read(1)
        if not c:
            break
        if c == "\n" or c == "\r":
            if PC.tampon:
                commande_pc(PC.tampon)
                PC.tampon = ""
        elif len(PC.tampon) < 64:
            PC.tampon += c


# -----------------------------------------------------------------------------
#  INITIALISATION ET BOUCLE PRINCIPALE
# -----------------------------------------------------------------------------
def initialiser_ecran():
    i2c = machine.SoftI2C(scl=machine.Pin(PIN_SCL), sda=machine.Pin(PIN_SDA),
                          freq=FREQ_I2C)
    trouves = i2c.scan()
    if ADRESSE_I2C not in trouves:
        raise RuntimeError("OLED introuvable en I2C (0x%02X). Peripheriques : %s"
                           % (ADRESSE_I2C, [hex(a) for a in trouves]))
    d = sh1106.SH1106_I2C(LARGEUR, HAUTEUR, i2c, addr=ADRESSE_I2C, rotate=180)
    d.fill(0)
    d.show()
    return d


def boucle_principale():
    d = initialiser_ecran()
    initialiser_boutons()
    initialiser_liaison_pc()
    demarrer_reseau()

    prochaine_image = ticks_ms()
    while True:
        t = ticks_ms()
        # --- services legers, appeles a chaque tour, qui ne font rien tant
        # --- que leur echeance n'est pas atteinte
        gestion_boutons(t)
        liaison_pc(t)
        minuteur(t)
        horloge(t)
        meteo(t)
        humeur(t)
        # --- animation cadencee (~30 images/s)
        if ticks_diff(t, prochaine_image) >= 0:
            yeux(d, t)
            prochaine_image = ticks_add(prochaine_image, PERIODE_IMAGE_MS)
            if ticks_diff(ticks_ms(), prochaine_image) > 0:   # en retard : on resynchronise
                prochaine_image = ticks_ms()
        time.sleep_ms(2)


if __name__ == "__main__":
    try:
        boucle_principale()
    except KeyboardInterrupt:
        print("Arret demande")
    except Exception as e:
        sys.print_exception(e)
        raise


