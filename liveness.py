import dlib
from scipy.spatial import distance as dist

# Prédicteur des 68 repères du visage (yeux, nez, bouche...). Le fichier
# .dat doit être téléchargé séparément (voir README).
_predictor = dlib.shape_predictor("shape_predictor_68_face_landmarks.dat")

# Indices des points des yeux dans les 68 repères du visage
LEFT_EYE = list(range(42, 48))
RIGHT_EYE = list(range(36, 42))

# Seuil en dessous duquel on considère l'œil "fermé"
EAR_THRESHOLD = 0.21
# Nombre d'images consécutives sous le seuil pour valider un vrai clignement
# (évite de compter un simple bruit de détection comme un clignement)
CONSEC_FRAMES = 2


def eye_aspect_ratio(eye):
    """
    Calcule le ratio d'ouverture de l'œil (EAR) à partir de 6 points de
    contour. Un œil grand ouvert donne un EAR élevé (~0.3), un œil fermé
    donne un EAR proche de 0.
    """
    a = dist.euclidean(eye[1], eye[5])
    b = dist.euclidean(eye[2], eye[4])
    c = dist.euclidean(eye[0], eye[3])
    return (a + b) / (2.0 * c)


class BlinkDetector:
    """
    Détecteur de clignement à état : on l'appelle image par image (via
    process) et il garde en mémoire le nombre d'images consécutives où
    l'œil est fermé, pour ne valider un clignement qu'une fois terminé.
    """

    def __init__(self):
        self.counter = 0
        self.blinked = False

    def process(self, gray, rect):
        """
        :param gray: image complète en niveaux de gris (pas un recadrage)
        :param rect: dlib.rectangle du visage dans cette image, déjà connu
            (évite de redétecter le visage, ce qui était source de bruit)
        """
        shape = _predictor(gray, rect)
        coords = [(shape.part(i).x, shape.part(i).y) for i in range(68)]
        left_eye = [coords[i] for i in LEFT_EYE]
        right_eye = [coords[i] for i in RIGHT_EYE]

        ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

        # On valide dès qu'une seule image montre l'œil fermé : le rythme
        # réel de traitement (limité par le calcul des repères du visage)
        # est souvent trop lent pour capturer plusieurs images consécutives
        # pendant un clignement, qui ne dure que 100 à 300 ms.
        if ear < EAR_THRESHOLD:
            self.blinked = True

        return self.blinked

    def reset(self):
        self.counter = 0
        self.blinked = False


class HeadMovementDetector:
    """
    Détecteur de mouvement de tête à état : suit la position du bout du
    nez (point 30 des 68 repères) sur une fenêtre glissante d'images, et
    valide un mouvement si le déplacement cumulé dépasse un seuil. Une
    photo figée ne peut pas produire ce mouvement naturellement.
    """

    NOSE_TIP = 30
    HISTORY_SIZE = 15       # nombre d'images gardées en mémoire
    MOVEMENT_THRESHOLD = 12  # déplacement minimal en pixels pour valider

    def __init__(self):
        self.positions = []
        self.moved = False

    def process(self, gray, rect):
        """
        :param gray: image complète en niveaux de gris
        :param rect: dlib.rectangle du visage dans cette image
        """
        shape = _predictor(gray, rect)
        nose = (shape.part(self.NOSE_TIP).x, shape.part(self.NOSE_TIP).y)

        self.positions.append(nose)
        if len(self.positions) > self.HISTORY_SIZE:
            self.positions.pop(0)

        if len(self.positions) >= 2:
            xs = [p[0] for p in self.positions]
            ys = [p[1] for p in self.positions]
            displacement = ((max(xs) - min(xs)) ** 2 + (max(ys) - min(ys)) ** 2) ** 0.5
            if displacement >= self.MOVEMENT_THRESHOLD:
                self.moved = True

        return self.moved

    def reset(self):
        self.positions = []
        self.moved = False