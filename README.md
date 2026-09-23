# Système de pointage par reconnaissance faciale avec anti-spoofing

Application desktop (Kivy) de gestion de présence par reconnaissance
faciale, avec une couche de sécurité anti-spoofing (détection de
vivacité) pour empêcher qu'une photo ou une vidéo soit utilisée pour
tromper le système.

## Fonctionnalités

- Reconnaissance faciale en temps réel via webcam (`face_recognition` / dlib)
- Anti-spoofing par détection de vivacité : clignement des yeux (EAR)
  **et** mouvement de tête, les deux signaux étant requis ensemble
- Ajout de nouvelles personnes directement depuis l'application
- Historique des pointages du jour, stocké en base SQLite

## Architecture

- `face_engine.py` — encodage et reconnaissance des visages
- `liveness.py` — anti-spoofing (clignement + mouvement de tête)
- `attendance_store.py` — stockage des pointages (SQLite)
- `camera_screen.py`, `add_person_screen.py`, `history_screen.py` — écrans Kivy
- `main.py` — point d'entrée, navigation entre les écrans

## Installation

```bash
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
```

### Modèle dlib requis

Télécharger `shape_predictor_68_face_landmarks.dat` depuis
[dlib-models](https://github.com/davisking/dlib-models) (fichier
`shape_predictor_68_face_landmarks.dat.bz2`), le décompresser, et
placer le fichier `.dat` à la racine du projet.

### Photos de référence

Créer un dossier `ImagesAttendance/` à la racine du projet, ou utiliser
l'écran "Ajouter une personne" de l'application une fois lancée.

## Lancement

```bash
python main.py
```

## Limites connues

- La détection de vivacité repose sur des indices comportementaux
  (clignement, mouvement) : elle peut en théorie être trompée par une
  vidéo (et non une simple photo) montrant la personne cligner des
  yeux. Une analyse de texture d'image serait une amélioration future
  possible pour détecter la présence d'un écran.
