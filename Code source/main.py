from machine import Pin, I2C
from time import sleep_ms
from sh1106 import SH1106_I2C
import wifi

from boutons import gauche, droite, ok
from pages import PAGES

# Initialisation de l'ecran
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
oled = SH1106_I2C(128, 64, i2c, None, 0x3C)

# Navigation
page_actuelle = 0
nombre_pages = len(PAGES)

# Afficher la premiere page
PAGES[page_actuelle](oled)

while True:

    if droite.appui():
        page_actuelle = (page_actuelle + 1) % nombre_pages
        PAGES[page_actuelle](oled)

    if gauche.appui():
        page_actuelle = (page_actuelle - 1) % nombre_pages
        PAGES[page_actuelle](oled)

    sleep_ms(10)

