import os
import numpy as np
import face_recognition


def load_known_faces(folder_path):
    """
    Parcourt un dossier d'images de référence (une photo par personne)
    et retourne deux listes alignées :
    - known_encodings : l'encodage facial (vecteur de 128 nombres qui
      représente le visage) de chaque personne
    - known_names : le nom correspondant, déduit du nom du fichier
    """
    known_encodings = []
    known_names = []

    for filename in os.listdir(folder_path):
        path = os.path.join(folder_path, filename)
        image = face_recognition.load_image_file(path)
        encodings = face_recognition.face_encodings(image)

        if len(encodings) == 0:
            print(f"Aucun visage détecté dans {filename}, image ignorée.")
            continue

        known_encodings.append(encodings[0])
        known_names.append(os.path.splitext(filename)[0])

    return known_encodings, known_names


def recognize_faces(frame, known_encodings, known_names, tolerance=0.5):
    """
    Prend une image (frame) de la webcam et retourne, pour chaque visage
    détecté, un tuple (nom, position) :
    - nom : le nom reconnu, ou "Inconnu" si aucune correspondance
    - position : (top, right, bottom, left), coordonnées du rectangle
      du visage dans l'image
    """
    face_locations = face_recognition.face_locations(frame)
    face_encodings = face_recognition.face_encodings(frame, face_locations)

    results = []
    for encoding, location in zip(face_encodings, face_locations):
        distances = face_recognition.face_distance(known_encodings, encoding)

        name = "Inconnu"
        if len(distances) > 0:
            best_match_index = np.argmin(distances)
            if distances[best_match_index] <= tolerance:
                name = known_names[best_match_index]

        results.append((name, location))

    return results


if __name__ == "__main__":
    encodings, names = load_known_faces("ImagesAttendance")
    print("Visages chargés :", names)
