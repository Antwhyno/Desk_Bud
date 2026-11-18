"""Logique des yeux et des expressions de Desk Bud.

Ce module ne touche pas a l'ecran : il calcule l'image et la dessine
dans le framebuffer qu'on lui donne. L'affichage (show) est fait par pages.py.

    yeux.mettre_a_jour(t)   -> True si l'image a change
    yeux.dessiner(oled)     -> dessine le visage (sans show)
    yeux.definir_expression("joyeuse")
    yeux.expression_suivante()
"""
import math
import random
import time

LARGEUR = 128
HAUTEUR = 64

# largeur, hauteur, paupiere haute, joue basse, largeur bouche,
# courbure bouche (positive = sourire), bouche ouverte
EXPRESSIONS = {
    "neutre":   (34, 36, 0,  0,  0,  0, 0),
    "joyeuse":  (34, 30, 0, 13, 22,  4, 0),
    "fatiguee": (34, 34, 13, 0,  0,  0, 0),
    "surprise": (36, 42, 0,  0, 10,  0, 3),
    "triste":   (34, 36, 5,  0, 14, -3, 0),
    "curieuse": (34, 34, 0,  0,  0,  0, 0),
    "endormie": (34, 36, 29, 0,  0,  0, 0),
}
ORDRE_EXPRESSIONS = tuple(EXPRESSIONS.keys())

_expression = "neutre"
_cible = list(EXPRESSIONS[_expression])
_valeurs = [float(v) for v in _cible]
_prochaine_humeur = time.ticks_add(time.ticks_ms(), 20000)
_prochaine_blink = time.ticks_add(time.ticks_ms(), 3000)
_blink = 1.0
_blink_seq = None
_blink_index = 0
_blink_temps = 0
_regard_x = 0.0
_regard_y = 0.0
_cible_x = 0.0
_cible_y = 0.0
_mouvement_debut = 0
_mouvement_duree = 1
_signature = None
_image = None   # derniere image calculee (parametres de dessin)


def definir_expression(nom):
    """Choisit une expression parmi neutre, joyeuse, fatiguee, surprise,
    triste, curieuse et endormie. Renvoie False si le nom est inconnu."""
    global _expression, _cible
    if nom not in EXPRESSIONS:
        return False
    _expression = nom
    _cible = list(EXPRESSIONS[nom])
    return True


def expression_suivante():
    """Passe a l'expression suivante de la liste."""
    i = ORDRE_EXPRESSIONS.index(_expression)
    definir_expression(ORDRE_EXPRESSIONS[(i + 1) % len(ORDRE_EXPRESSIONS)])


def _arrondir(valeur):
    return int(valeur + 0.5) if valeur >= 0 else -int(-valeur + 0.5)


def _borner(valeur, minimum, maximum):
    return max(minimum, min(maximum, valeur))


def _rectangle(d, x, y, largeur, hauteur, couleur):
    x, y = int(x), int(y)
    largeur, hauteur = int(largeur), int(hauteur)
    if x < 0:
        largeur += x
        x = 0
    if y < 0:
        hauteur += y
        y = 0
    largeur = min(largeur, LARGEUR - x)
    hauteur = min(hauteur, HAUTEUR - y)
    if largeur > 0 and hauteur > 0:
        d.fill_rect(x, y, largeur, hauteur, couleur)


def _disque(d, cx, cy, rayon, couleur):
    for dy in range(-rayon, rayon + 1):
        dx = int(math.sqrt(max(0, rayon * rayon - dy * dy)))
        _rectangle(d, cx - dx, cy + dy, 2 * dx + 1, 1, couleur)


def _oeil(d, centre_x, centre_y, largeur, hauteur, paupiere):
    x = int(centre_x - largeur / 2)
    y = int(centre_y - hauteur / 2)
    # Forme douce : rectangle central et quatre coins arrondis.
    rayon = min(8, largeur // 4, hauteur // 4)
    _rectangle(d, x + rayon, y, largeur - 2 * rayon, hauteur, 1)
    _rectangle(d, x, y + rayon, largeur, hauteur - 2 * rayon, 1)
    for ox, oy in ((rayon, rayon), (largeur-rayon-1, rayon),
                   (rayon, hauteur-rayon-1),
                   (largeur-rayon-1, hauteur-rayon-1)):
        _disque(d, x + ox, y + oy, rayon, 1)
    if paupiere > 0:
        _rectangle(d, x, y, largeur, min(hauteur, int(paupiere)), 0)


def _bouche(d, cx, cy, largeur, courbure, ouverture):
    if ouverture >= 1:
        _disque(d, cx, cy, ouverture, 1)
    elif largeur >= 3:
        demi = largeur // 2
        for dx in range(-demi, demi + 1):
            y = cy + _arrondir(courbure * (1 - (dx * dx) / (demi * demi)))
            _rectangle(d, cx + dx, y, 1, 2, 1)


def _animer_regard(t):
    global _regard_x, _regard_y, _cible_x, _cible_y
    global _mouvement_debut, _mouvement_duree
    ecoule = time.ticks_diff(t, _mouvement_debut)

    # Une duree nulle signifie que le regard attend sa prochaine cible.
    if _mouvement_duree == 0:
        if ecoule >= 0:
            _cible_x = random.uniform(-1, 1)
            _cible_y = random.uniform(-0.5, 0.5)
            _mouvement_debut = t
            _mouvement_duree = random.randint(180, 450)
        return

    if ecoule >= _mouvement_duree:
        _regard_x, _regard_y = _cible_x, _cible_y
        # Pause entre deux mouvements du regard (plus longue = plus calme)
        _mouvement_debut = time.ticks_add(t, random.randint(1500, 5000))
        _mouvement_duree = 0
    else:
        p = max(0.0, ecoule / _mouvement_duree)
        p = (1 - math.cos(math.pi * p)) / 2
        _regard_x += (_cible_x - _regard_x) * p
        _regard_y += (_cible_y - _regard_y) * p


def _animer_clignement(t):
    global _blink, _blink_seq, _blink_index, _blink_temps, _prochaine_blink
    if _blink_seq is not None:
        if time.ticks_diff(t, _blink_temps) >= 18:
            _blink_temps = t
            _blink_index += 1
            if _blink_index >= len(_blink_seq):
                _blink_seq = None
                _blink = 1.0
                # Delai entre deux clignements
                _prochaine_blink = time.ticks_add(t, random.randint(3000, 8000))
            else:
                _blink = _blink_seq[_blink_index]
    elif time.ticks_diff(t, _prochaine_blink) >= 0:
        _blink_seq = (0.7, 0.35, 0.08, 0.08, 0.4, 0.75, 1.0)
        _blink_index = 0
        _blink_temps = t
        _blink = _blink_seq[0]


def _preparer(t):
    """Calcule l'image. Renvoie True si elle a change depuis la derniere fois."""
    global _signature, _image
    largeur, hauteur, haut, bas, bouche_l, courbe, ouverture = _valeurs
    # Valeurs arrondies : sinon l'image semble "changer" a chaque tour
    largeur = _arrondir(largeur)
    bouche_l = _arrondir(bouche_l)
    ouverture = _arrondir(ouverture)
    dx = _arrondir(_regard_x * 7)
    dy = _arrondir(_regard_y * 3)
    if _expression == "endormie":
        dy += _arrondir(math.sin(t / 700) * 1.5)
    haut = haut * _blink
    hauteur_oeil = max(2, _arrondir(hauteur * _blink))
    centres_y = 29 + dy
    gauche = 64 - 30 + dx
    droite = 64 + 30 + dx
    sig = (largeur, hauteur_oeil, _arrondir(haut), _arrondir(bas * _blink),
           _expression, dx, dy, _arrondir(courbe), bouche_l, ouverture)
    if sig == _signature:
        return False
    _signature = sig
    _image = (gauche, droite, centres_y, largeur, hauteur_oeil, haut,
              bas, bouche_l, courbe, ouverture, dx, dy)
    return True


def dessiner(d):
    """Dessine le visage dans le framebuffer de d (sans appeler show)."""
    if _image is None:
        return
    (gauche, droite, centres_y, largeur, hauteur_oeil, haut,
     bas, bouche_l, courbe, ouverture, dx, dy) = _image
    d.fill(0)
    _oeil(d, gauche, centres_y, largeur, hauteur_oeil, haut)
    _oeil(d, droite, centres_y, largeur, hauteur_oeil, haut)
    if bas > 0:
        _disque(d, gauche, centres_y + hauteur_oeil // 2 + 13, 23, 0)
        _disque(d, droite, centres_y + hauteur_oeil // 2 + 13, 23, 0)
    _bouche(d, 64 + dx // 2, 57 + dy // 2, bouche_l, courbe, ouverture)


def mettre_a_jour(t=None):
    """Fait avancer l'animation. Renvoie True si l'image a change
    (il faut alors appeler dessiner puis oled.show)."""
    global _prochaine_humeur
    if t is None:
        t = time.ticks_ms()
    for i in range(len(_valeurs)):
        _valeurs[i] += (_cible[i] - _valeurs[i]) * 0.2
    _animer_regard(t)
    _animer_clignement(t)
    # Petites expressions spontanees lorsque l'expression est neutre.
    if _expression == "neutre" and time.ticks_diff(t, _prochaine_humeur) >= 0:
        nom = "joyeuse" if random.random() < 0.6 else "curieuse"
        definir_expression(nom)
        _prochaine_humeur = time.ticks_add(t, random.randint(1800, 3500))
    elif _expression != "neutre" and time.ticks_diff(t, _prochaine_humeur) >= 0:
        definir_expression("neutre")
        _prochaine_humeur = time.ticks_add(t, random.randint(15000, 45000))
    return _preparer(t)
