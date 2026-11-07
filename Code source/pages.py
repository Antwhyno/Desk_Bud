
# pages.py
# Toutes les pages de notre mini-station meteo

from meteo import obtenir_meteo, meteo_en_cache
from animation import chargement
from dessins import afficher_meteo, texte_grand


# ---------------------------------
# Fonction commune : en-tete
# ---------------------------------

def entete(oled, titre):
    oled.fill(1)                    # Fond blanc
    oled.text(titre, 0, 0, 0)       # Texte noir
    oled.hline(0, 11, 128, 0)      # Ligne noire


# ---------------------------------
# Page 1 : Accueil
# ---------------------------------

def accueil(oled):
    entete(oled, "ACCUEIL")

    oled.text("Mini station", 12, 22, 0)
    oled.text("meteo ESP32", 12, 34, 0)
    oled.text("<        >", 20, 54, 0)

    oled.show()


# ---------------------------------
# Page 2 : Parametres
# ---------------------------------

def parametres(oled):
    entete(oled, "PARAMETRES")

    oled.text("Wi-Fi : actif", 0, 20, 0)
    oled.text("Ecran : SH1106", 0, 32, 0)
    oled.text("Mode : blanc", 0, 44, 0)

    oled.show()


# ---------------------------------
# Page 3 : Informations
# ---------------------------------

def informations(oled):
    entete(oled, "INFORMATIONS")

    oled.text("ESP32-C3", 0, 20, 0)
    oled.text("OLED 128x64", 0, 32, 0)
    oled.text("MicroPython", 0, 44, 0)

    oled.show()


# ---------------------------------
# Page 4 : Meteo
# ---------------------------------

def page_meteo(oled):

    # Afficher le chargement seulement
    # si les donnees ne sont pas en cache
    if not meteo_en_cache():
        chargement(oled, 30)

    # Recuperer les donnees Open-Meteo
    meteo = obtenir_meteo()

    entete(oled, "METEO")

    # Si la meteo est indisponible
    if meteo is None:
        oled.text("Connexion", 12, 25, 0)
        oled.text("impossible", 12, 37, 0)
        oled.show()
        return

    # Recuperer les valeurs
    temperature = round(meteo["temperature_2m"])
    humidite = round(meteo["relative_humidity_2m"])
    vent = round(meteo["wind_speed_10m"])
    code = meteo["weather_code"]

    # Temperature
    texte_temperature = str(temperature)

    if len(texte_temperature) < 2:
        texte_temperature = "0" + texte_temperature

    texte_grand(oled, texte_temperature, 4, 21, 3, 0)
    texte_grand(oled, "C", 53,21,3,0)
    # Icone meteo 32x32
    afficher_meteo(oled, code, 88, 15)

    # Separation
    oled.hline(0, 49, 128, 0)

    # Humidite et vitesse du vent
    oled.text("H:" + str(humidite) + "%", 0, 55, 0)
    oled.text("V:" + str(vent), 72, 55, 0)

    oled.show()


# ---------------------------------
# Liste des pages pour main.py
# ---------------------------------

PAGES = [
    accueil,
    parametres,
    informations,
    page_meteo
]
