from machine import Pin, SoftI2C
from time import sleep_ms, ticks_ms, ticks_diff
import gc
import sys

from config import OLED_SDA, OLED_SCL, OLED_ADRESSE, OLED_LARGEUR, OLED_HAUTEUR
from sh1106 import SH1106_I2C

# ===== 1. ECRAN (d'abord, pour pouvoir afficher des messages) =====
i2c = SoftI2C(sda=Pin(OLED_SDA), scl=Pin(OLED_SCL), freq=100000)
oled = SH1106_I2C(OLED_LARGEUR, OLED_HAUTEUR, i2c, None, OLED_ADRESSE, rotate=180)

# ===== 2. WI-FI (wifi.py se connecte quand on l'importe, jusqu'a ~20 s) =====
oled.fill(0)
oled.text("Connexion", 28, 20, 1)
oled.text("Wi-Fi...", 32, 34, 1)
oled.show()
import wifi

# ===== 3. LE RESTE =====
import yeux
from boutons import gauche, droite, ok
from pages import PAGES

NB_ECRANS = len(PAGES) + 1      # ecran 0 = les yeux, puis les pages
ecran = 0
expression = 0


def afficher(numero):
    gc.collect()
    if numero == 0:
        yeux._signature = None  # force le redessin complet du visage
        return
    try:
        PAGES[numero - 1](oled)
    except Exception as e:      # une page en erreur ne doit pas tout arreter
        sys.print_exception(e)
        oled.fill(0)
        oled.text("Erreur page", 0, 20, 1)
        oled.text("voir Thonny", 0, 34, 1)
        oled.show()


yeux.definir_expression("joyeuse")
afficher(ecran)
derniere_image = ticks_ms()

while True:
    t = ticks_ms()

    if droite.appui():
        ecran = (ecran + 1) % NB_ECRANS
        afficher(ecran)

    if gauche.appui():
        ecran = (ecran - 1) % NB_ECRANS
        afficher(ecran)

    if ok.appui() and ecran == 0:
        expression = (expression + 1) % len(yeux.ORDRE_EXPRESSIONS)
        yeux.definir_expression(yeux.ORDRE_EXPRESSIONS[expression])

    # Animation des yeux (~30 ms entre deux images), seulement sur l'ecran 0
    if ecran == 0 and ticks_diff(t, derniere_image) >= 30:
        yeux.mettre_a_jour(oled, t)
        derniere_image = t

    sleep_ms(5)
