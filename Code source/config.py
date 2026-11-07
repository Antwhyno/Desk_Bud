from machine import Pin

# ===== BROCHES DES BOUTONS =====
PIN_GAUCHE = 1
PIN_DROITE = 3
PIN_OK = 2

# ===== INITIALISATION DES BOUTONS =====
BTN_GAUCHE = Pin(PIN_GAUCHE, Pin.IN, Pin.PULL_UP)#IN = Entrer     PULL_UP=laisse la valeur entre 0 et 1
BTN_DROITE = Pin(PIN_DROITE, Pin.IN, Pin.PULL_UP)
BTN_OK = Pin(PIN_OK, Pin.IN, Pin.PULL_UP)

# ===== ECRAN SH1106 =====
OLED_SDA = 8
OLED_SCL = 9
OLED_ADRESSE = 0x3C
OLED_LARGEUR = 128
OLED_HAUTEUR = 64

# ===== PARAMETRES =====
ANTI_REBOND_MS = 35 # évite que le bouton soit lu commme appuyer plusieurs fois