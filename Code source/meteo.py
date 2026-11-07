import urequests
from time import ticks_ms, ticks_diff

URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude=47.3319&longitude=5.0322"
    "&current=temperature_2m,apparent_temperature,"
    "relative_humidity_2m,precipitation,"
    "weather_code,wind_speed_10m"
    "&temperature_unit=celsius"
    "&timezone=Europe%2FParis"
)

donnees = None
derniere_maj = None

def obtenir_meteo():
    global donnees, derniere_maj

    # Garder les donnees pendant 10 minutes
    if derniere_maj is not None:
        if ticks_diff(ticks_ms(), derniere_maj) < 600000:
            return donnees

    reponse = None

    try:
        reponse = urequests.get(URL)
        resultat = reponse.json()

        donnees = resultat["current"]
        derniere_maj = ticks_ms()

        return donnees

    except Exception as erreur:
        print("Erreur meteo :", erreur)
        return donnees

    finally:
        if reponse is not None:
            reponse.close()
            
            
def meteo_en_cache():
    if donnees is None or derniere_maj is None:
        return False

    return ticks_diff(ticks_ms(), derniere_maj) < 600000