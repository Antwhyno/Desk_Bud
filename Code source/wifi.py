import network
from time import sleep_ms

SSID = "Nom du réseau"
MOT_DE_PASSE = "Mot de passe"

def connexion_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)

    if not wlan.isconnected():
        print("Connexion Wi-Fi...")
        wlan.connect(SSID, MOT_DE_PASSE)

        for i in range(100):
            if wlan.isconnected():
                break
            sleep_ms(200)

    if wlan.isconnected():
        print("Wi-Fi connecte !")
        print("IP :", wlan.ifconfig()[0])
        return True

    print("Connexion impossible :", wlan.status())
    return False

connexion_wifi()
