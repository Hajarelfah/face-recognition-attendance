import os
import cv2
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.graphics.texture import Texture

KNOWN_FACES_DIR = "ImagesAttendance"


class AddPersonScreen(Screen):
    """
    Écran d'ajout d'une nouvelle personne : aperçu caméra en direct,
    champ pour le nom, et bouton pour capturer une photo de référence.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical")

        self.image_widget = Image()
        layout.add_widget(self.image_widget)

        self.name_input = TextInput(
            hint_text="Nom complet de la personne",
            multiline=False,
            size_hint_y=0.1,
        )
        layout.add_widget(self.name_input)

        self.capture_button = Button(text="Capturer et enregistrer", size_hint_y=0.1)
        self.capture_button.bind(on_press=self.capture_and_save)
        layout.add_widget(self.capture_button)

        self.status_label = Label(text="", size_hint_y=0.1)
        layout.add_widget(self.status_label)

        self.add_widget(layout)

        self.capture = None
        self._event = None
        self._last_frame = None

    def on_enter(self):
        self.capture = cv2.VideoCapture(0)
        self._event = Clock.schedule_interval(self.update, 1.0 / 15.0)

    def on_leave(self):
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
        self._last_frame = frame
        self._display_frame(frame)

    def _display_frame(self, frame):
        display = cv2.flip(frame, 0)
        buf = display.tobytes()
        texture = Texture.create(size=(display.shape[1], display.shape[0]), colorfmt="bgr")
        texture.blit_buffer(buf, colorfmt="bgr", bufferfmt="ubyte")
        self.image_widget.texture = texture

    def capture_and_save(self, instance):
        name = self.name_input.text.strip()
        if not name:
            self.status_label.text = "Entre un nom avant de capturer."
            return
        if self._last_frame is None:
            self.status_label.text = "Aucune image caméra disponible."
            return

        if not os.path.exists(KNOWN_FACES_DIR):
            os.makedirs(KNOWN_FACES_DIR)

        path = os.path.join(KNOWN_FACES_DIR, f"{name}.jpg")
        cv2.imwrite(path, self._last_frame)

        # Recharge les visages connus dans l'écran caméra pour que la
        # nouvelle personne soit reconnue immédiatement, sans redémarrer
        camera_screen = self.manager.get_screen("camera")
        camera_screen.reload_known_faces()

        self.status_label.text = f"{name} enregistré(e) avec succès."
        self.name_input.text = ""
