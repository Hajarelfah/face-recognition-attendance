import cv2
import dlib
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture

from face_engine import load_known_faces, recognize_faces
from liveness import BlinkDetector, HeadMovementDetector
from attendance_store import init_db, already_marked_today, mark_attendance

KNOWN_FACES_DIR = "ImagesAttendance"


class CameraScreen(Screen):
    """
    Écran principal : flux caméra en direct, reconnaissance faciale,
    vérification de vivacité (anti-spoofing) et pointage automatique.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical")
        self.image_widget = Image()
        layout.add_widget(self.image_widget)

        self.status_label = Label(text="En attente...", size_hint_y=0.1)
        layout.add_widget(self.status_label)

        self.add_widget(layout)

        init_db()
        self.known_encodings, self.known_names = load_known_faces(KNOWN_FACES_DIR)

        # Une paire de détecteurs (clignement, mouvement) indépendante par
        # personne reconnue
        self.liveness_detectors = {}

        self.capture = None
        self._event = None

    def reload_known_faces(self):
        """Recharge les visages de référence (appelé après l'ajout d'une
        nouvelle personne depuis l'écran AddPersonScreen)."""
        self.known_encodings, self.known_names = load_known_faces(KNOWN_FACES_DIR)

    def on_enter(self):
        """Ouvre la caméra quand on arrive sur cet écran."""
        self.capture = cv2.VideoCapture(0)
        self._event = Clock.schedule_interval(self.update, 1.0 / 15.0)

    def on_leave(self):
        """Libère la caméra quand on quitte cet écran, pour que
        AddPersonScreen puisse l'utiliser à son tour."""
        if self._event:
            self._event.cancel()
            self._event = None
        if self.capture:
            self.capture.release()
            self.capture = None

    def update(self, dt):
        ret, frame = self.capture.read()
        if not ret:
            return

        results = recognize_faces(frame, self.known_encodings, self.known_names)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        for name, (top, right, bottom, left) in results:
            color = (0, 255, 0) if name != "Inconnu" else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(
                frame, name, (left, max(top - 10, 0)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2,
            )

            if name != "Inconnu":
                self._check_liveness_and_mark(name, gray, top, right, bottom, left)

        self._display_frame(frame)

    def _check_liveness_and_mark(self, name, gray, top, right, bottom, left):
        if name not in self.liveness_detectors:
            self.liveness_detectors[name] = (BlinkDetector(), HeadMovementDetector())

        blink_detector, movement_detector = self.liveness_detectors[name]
        rect = dlib.rectangle(left=left, top=top, right=right, bottom=bottom)

        blinked = blink_detector.process(gray, rect)
        moved = movement_detector.process(gray, rect)

        if not (blinked and moved):
            # Affiche l'état courant des deux signaux pour voir lequel manque
            self.status_label.text = (
                f"{name} — clignement: {'OK' if blinked else '...'} "
                f"| mouvement: {'OK' if moved else '...'}"
            )
            return

        if already_marked_today(name, "Présent"):
            self.status_label.text = f"{name} déjà pointé aujourd'hui"
        else:
            mark_attendance(name, "Présent")
            self.status_label.text = f"{name} pointé (vivacité confirmée: clignement + mouvement)"

        blink_detector.reset()
        movement_detector.reset()

    def _display_frame(self, frame):
        frame = cv2.flip(frame, 0)
        buf = frame.tobytes()
        texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.image_widget.texture = texture