from time import ticks_ms, ticks_diff
from meteo import obtenir_meteo, meteo_en_cache
from animation import chargement
from dessins import afficher_meteo, texte_grand
import yeux

# Mode nuit : fond noir, texte blanc (inversion faite par le programme,
# sans utiliser oled.invert). Mets True pour démarrer en mode nuit.
_nuit = True


def fond():
    return 0 if _nuit else 1


def encre():
    return 1 if _nuit else 0


def basculer_nuit():
    global _nuit
    _nuit = not _nuit


def entete(oled, titre):
    oled.fill(fond())
    oled.text(titre, 0, 0, encre())
    oled.hline(0, 11, 128, encre())


def page_yeux(oled):
    yeux.mettre_a_jour(ticks_ms())
    yeux.dessiner(oled)
    oled.show()


def accueil(oled):
    entete(oled, "ACCUEIL")

    oled.text("Mini station", 12, 22, encre())
    oled.text("meteo ESP32", 12, 34, encre())
    oled.text("<        >", 20, 54, encre())

    oled.show()


def parametres(oled):
    entete(oled, "PARAMETRES")

    oled.text("Wi-Fi : actif", 0, 20, encre())
    oled.text("Ecran : SH1106", 0, 32, encre())
    oled.text("Mode : nuit" if _nuit else "Mode : blanc", 0, 44, encre())

    oled.show()


def informations(oled):
    entete(oled, "INFORMATIONS")

    oled.text("ESP32-C3", 0, 20, encre())
    oled.text("OLED 128x64", 0, 32, encre())
    oled.text("MicroPython", 0, 44, encre())

    oled.show()


def page_meteo(oled):

    if not meteo_en_cache():
        chargement(oled, 30)

    meteo = obtenir_meteo()

    entete(oled, "METEO")

    if meteo is None:
        oled.text("Connexion", 12, 25, encre())
        oled.text("impossible", 12, 37, encre())
        oled.show()
        return

    temperature = round(meteo["temperature_2m"])
    humidite = round(meteo["relative_humidity_2m"])
    vent = round(meteo["wind_speed_10m"])
    code = meteo["weather_code"]

    texte_temperature = str(temperature)

    if len(texte_temperature) < 2:
        texte_temperature = "0" + texte_temperature

    texte_grand(oled, texte_temperature, 4, 21, 3, encre())
    texte_grand(oled, "C", 53, 21, 3, encre())

    afficher_meteo(oled, code, 88, 15, _nuit)

    oled.hline(0, 49, 128, encre())

    oled.text("H:" + str(humidite) + "%", 0, 55, encre())
    oled.text("V:" + str(vent), 72, 55, encre())

    oled.show()


PAGES = [
    page_yeux,
    accueil,
    parametres,
    informations,
    page_meteo
]

_dernier_rafraichissement = 0


def afficher(oled, numero):
    oled.invert(0)      # on n'utilise plus l'inversion matérielle
    PAGES[numero](oled)


def rafraichir(oled, numero, t):
    global _dernier_rafraichissement
    if PAGES[numero] is page_yeux:
        if ticks_diff(t, _dernier_rafraichissement) >= 50:   # ~20 images/s
            _dernier_rafraichissement = t
            if yeux.mettre_a_jour(t):
                yeux.dessiner(oled)
                oled.show()


def bouton_ok(oled, numero):
    if PAGES[numero] is page_yeux:
        yeux.expression_suivante()
    elif PAGES[numero] is parametres:
        basculer_nuit()
        parametres(oled)