from time import ticks_ms, ticks_diff
from config import (
    BTN_GAUCHE,
    BTN_DROITE,
    BTN_OK,
    ANTI_REBOND_MS
) # importe le nom des broches


class Bouton:
    def __init__(self, pin):
        self.pin = pin
        self.dernier_etat = pin.value()
        self.etat_stable = pin.value()
        self.dernier_changement = ticks_ms()

    def appui(self):
        maintenant = ticks_ms()
        etat = self.pin.value()

        # Detecter un changement electrique
        if etat != self.dernier_etat:
            self.dernier_changement = maintenant
            self.dernier_etat = etat

        # Verifier que le signal est stable
        if ticks_diff(maintenant,self.dernier_changement) >= ANTI_REBOND_MS:

            if etat != self.etat_stable:
                self.etat_stable = etat

                # Bouton appuye (PULL_UP)
                if etat == 0:
                    return True

        return False


# Creation des trois boutons
gauche = Bouton(BTN_GAUCHE)
droite = Bouton(BTN_DROITE)
ok = Bouton(BTN_OK)
