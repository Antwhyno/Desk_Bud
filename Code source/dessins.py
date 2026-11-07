# dessins.py - icones 32x32, pixels noirs sur fond blanc
import framebuf

NOMS_ICONES = (
    "nuage", "eclaircies", "soleil", "pluie", "averses",
    "brouillard", "orage", "neige", "vent"
)

def afficher_icone(oled, nom, x, y):
    if nom not in NOMS_ICONES:
        nom = "nuage"
    with open("icones/" + nom + ".bin", "rb") as fichier:
        pixels = bytearray(fichier.read())
    image = framebuf.FrameBuffer(pixels, 32, 32, framebuf.MONO_HLSB)
    oled.blit(image, x, y)

def icone_pour_code(code):
    if code == 0:
        return "soleil"
    if code in (1, 2):
        return "eclaircies"
    if code == 3:
        return "nuage"
    if code in (45, 48):
        return "brouillard"
    if code in (51, 53, 55, 56, 57, 61, 63, 65, 66, 67):
        return "pluie"
    if code in (80, 81, 82):
        return "averses"
    if code in (71, 73, 75, 77, 85, 86):
        return "neige"
    if code in (95, 96, 99):
        return "orage"
    return "nuage"

def afficher_meteo(oled, code, x, y):
    afficher_icone(oled, icone_pour_code(code), x, y)
    

import framebuf

def texte_grand(oled, texte, x, y, taille=2, couleur=0):
    # Transformer le texte en chaine de caracteres
    texte = str(texte)

    # Creer une petite image de 8x8 pixels
    tampon = bytearray(8)
    caractere = framebuf.FrameBuffer(
        tampon, 8, 8, framebuf.MONO_HLSB
    )

    # Parcourir chaque lettre ou chiffre
    for lettre in texte:
        caractere.fill(0)
        caractere.text(lettre, 0, 0, 1)

        # Agrandir les pixels du caractere
        for py in range(8):
            for px in range(8):
                if caractere.pixel(px, py):
                    oled.fill_rect(
                        x + px * taille,
                        y + py * taille,
                        taille,
                        taille,
                        couleur
                    )

        # Avancer vers le caractere suivant
        x += 8 * taille
