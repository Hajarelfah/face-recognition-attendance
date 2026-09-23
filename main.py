from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager

from camera_screen import CameraScreen
from add_person_screen import AddPersonScreen
from history_screen import HistoryScreen


class RootLayout(BoxLayout):
    """
    Widget racine : une barre de navigation en haut (3 boutons) et un
    ScreenManager en dessous qui affiche l'écran actif.
    """

    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", **kwargs)

        nav_bar = BoxLayout(size_hint_y=0.08)
        self.add_widget(nav_bar)

        self.screen_manager = ScreenManager()
        self.screen_manager.add_widget(CameraScreen(name="camera"))
        self.screen_manager.add_widget(AddPersonScreen(name="add_person"))
        self.screen_manager.add_widget(HistoryScreen(name="history"))
        self.add_widget(self.screen_manager)

        nav_items = [
            ("Caméra / Pointage", "camera"),
            ("Ajouter une personne", "add_person"),
            ("Historique du jour", "history"),
        ]
        for label, screen_name in nav_items:
            btn = Button(text=label)
            btn.bind(on_press=lambda instance, s=screen_name: self.switch_to(s))
            nav_bar.add_widget(btn)

    def switch_to(self, screen_name):
        self.screen_manager.current = screen_name


class AttendanceApp(App):
    def build(self):
        return RootLayout()


if __name__ == "__main__":
    AttendanceApp().run()