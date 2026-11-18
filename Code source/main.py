from machine import Pin, SoftI2C
from time import sleep_ms, ticks_ms
import gc
import sys

from config import OLED_SDA, OLED_SCL, OLED_ADRESSE, OLED_LARGEUR, OLED_HAUTEUR
from sh1106 import SH1106_I2C

# ===== Ecran =====
# 400 kHz : affichage ~4x plus rapide. Si l'ecran est instable, mettre 100000.
i2c = SoftI2C(sda=Pin(OLED_SDA), scl=Pin(OLED_SCL), freq=400000)
oled = SH1106_I2C(OLED_LARGEUR, OLED_HAUTEUR, i2c, None, OLED_ADRESSE, rotate=180)
oled.contrast(0)   # 0 = très sombre, 255 = max (défaut : 127)

# ===== Wi-Fi (wifi.py se connecte a l'import) =====
oled.fill(0)
oled.text("Connexion", 28, 20, 1)
oled.text("Wi-Fi...", 32, 34, 1)
oled.show()
import wifi

# ===== Boutons, pages, yeux =====
from boutons import gauche, droite, ok
import pages
import yeux

yeux.definir_expression("joyeuse")

# ===== Navigation =====
page_actuelle = 0
nombre_pages = len(pages.PAGES)


def changer_page(numero):
    gc.collect()
    try:
        pages.afficher(oled, numero)
    except Exception as e:      # une page en erreur ne bloque pas le reste
        sys.print_exception(e)
        oled.fill(0)
        oled.text("Erreur page", 0, 20, 1)
        oled.text("voir Thonny", 0, 34, 1)
        oled.show()


changer_page(page_actuelle)

while True:
    t = ticks_ms()

    if droite.appui():
        page_actuelle = (page_actuelle + 1) % nombre_pages
        changer_page(page_actuelle)

    if gauche.appui():
        page_actuelle = (page_actuelle - 1) % nombre_pages
        changer_page(page_actuelle)

    if ok.appui():
        pages.bouton_ok(oled, page_actuelle)

    pages.rafraichir(oled, page_actuelle, t)

    sleep_ms(5)
