def chargement(oled, progression):
    oled.fill(0)

    oled.text("CHARGEMENT...", 8, 15)

    # Contour de la barre
    oled.rect(14, 38, 100, 12, 1)

    # Remplissage de la barre
    largeur = int(progression * 96 / 100)
    oled.fill_rect(16, 40, largeur, 8, 1)

    oled.show()