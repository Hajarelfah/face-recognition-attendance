from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button

from attendance_store import get_today_records


class HistoryScreen(Screen):
    """Écran listant les pointages du jour, avec un bouton pour rafraîchir."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = BoxLayout(orientation="vertical")

        refresh_button = Button(text="Rafraîchir", size_hint_y=0.1)
        refresh_button.bind(on_press=lambda instance: self.refresh())
        layout.add_widget(refresh_button)

        self.scroll = ScrollView()
        self.grid = GridLayout(cols=3, size_hint_y=None, spacing=4, padding=4)
        self.grid.bind(minimum_height=self.grid.setter("height"))
        self.scroll.add_widget(self.grid)
        layout.add_widget(self.scroll)

        self.add_widget(layout)

    def on_enter(self):
        self.refresh()

    def refresh(self):
        self.grid.clear_widgets()

        for header in ("Nom", "Horodatage", "Statut"):
            self.grid.add_widget(Label(text=header, bold=True, size_hint_y=None, height=30))

        records = get_today_records()
        if not records:
            self.grid.add_widget(Label(text="Aucun pointage aujourd'hui", size_hint_y=None, height=30))
            self.grid.add_widget(Label(text="", size_hint_y=None, height=30))
            self.grid.add_widget(Label(text="", size_hint_y=None, height=30))
            return

        for name, timestamp, status in records:
            self.grid.add_widget(Label(text=name, size_hint_y=None, height=30))
            self.grid.add_widget(Label(text=timestamp, size_hint_y=None, height=30))
            self.grid.add_widget(Label(text=status, size_hint_y=None, height=30))
