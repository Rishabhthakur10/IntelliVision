import dlib
import numpy as np
import cv2
import face_recognition_models
from sklearn.svm import SVC
import streamlit as st

from src.database.db import get_all_students


@st.cache_resource
def load_dlib_models():
    detector = dlib.get_frontal_face_detector()
    sp = dlib.shape_predictor(face_recognition_models.pose_predictor_model_location())
    facerec = dlib.face_recognition_model_v1(face_recognition_models.face_recognition_model_location())
    return detector, sp, facerec


def get_face_embeddings(image_np):
    """
    Detects faces in image_np and extracts 128-dimensional facial embeddings.
    Returns: (encodings, boxes) where boxes are (left, top, right, bottom).
    """
    try:
        detector, sp, facerec = load_dlib_models()
        # Convert to uint8 RGB if needed
        if image_np.dtype != np.uint8:
            image_np = image_np.astype(np.uint8)

        faces = detector(image_np, 1)

        encodings = []
        boxes = []

        for face in faces:
            shape = sp(image_np, face)
            face_descriptor = facerec.compute_face_descriptor(image_np, shape, 1)
            encodings.append(np.array(face_descriptor))
            boxes.append((face.left(), face.top(), face.right(), face.bottom()))

        return encodings, boxes
    except Exception as e:
        print(f"Error extracting face embeddings: {e}")
        return [], []


@st.cache_resource
def get_trained_model():
    X = []
    y = []

    student_db = get_all_students()
    if not student_db:
        return None

    for student in student_db:
        embedding = student.get("face_embedding")
        if embedding:
            X.append(np.array(embedding))
            y.append(student.get("student_id"))

    if len(X) == 0:
        return None

    clf = None
    unique_labels = sorted(list(set(y)))

    if len(unique_labels) >= 2:
        clf = SVC(kernel="linear", probability=True, class_weight="balanced")
        try:
            clf.fit(X, y)
        except Exception as e:
            print(f"Error training SVC: {e}")
            clf = None

    return {"clf": clf, "X": X, "y": y, "unique_labels": unique_labels}


def train_classifier():
    st.cache_resource.clear()
    model_data = get_trained_model()
    return bool(model_data)


def predict_attendance(class_image_np):
    """
    Scans class image, identifies enrolled students, and generates an annotated image
    with detection bounding boxes and confidence labels.
    Returns: (detected_student_dict, all_student_ids, num_faces, annotated_image_np)
    """
    encodings, boxes = get_face_embeddings(class_image_np)
    detected_student = {}

    annotated_img = class_image_np.copy()
    if annotated_img.dtype != np.uint8:
        annotated_img = annotated_img.astype(np.uint8)

    model_data = get_trained_model()
    if not model_data or not encodings:
        return detected_student, [], len(encodings), annotated_img

    clf = model_data.get("clf")
    X_train = model_data.get("X", [])
    y_train = model_data.get("y", [])
    all_students = model_data.get("unique_labels", [])

    # Cache student map for quick name lookups
    all_student_records = {s["student_id"]: s["name"] for s in get_all_students()}

    for encoding, box in zip(encodings, boxes):
        left, top, right, bottom = box

        if clf is not None and len(all_students) >= 2:
            predicted_id = int(clf.predict([encoding])[0])
        elif len(all_students) > 0:
            predicted_id = int(all_students[0])
        else:
            continue

        # Compute Euclidean distance to student's registered embedding
        try:
            target_indices = [idx for idx, sid in enumerate(y_train) if sid == predicted_id]
            if not target_indices:
                continue

            # Minimum distance among samples for this student
            best_dist = min([np.linalg.norm(X_train[idx] - encoding) for idx in target_indices])
            resemblance_threshold = 0.60

            student_name = all_student_records.get(predicted_id, f"ID #{predicted_id}")

            if best_dist <= resemblance_threshold:
                confidence = max(0, min(100, int((1.0 - (best_dist / resemblance_threshold)) * 40 + 60)))
                detected_student[predicted_id] = {
                    "name": student_name,
                    "confidence": f"{confidence}%",
                    "box": box
                }
                # Draw recognized bounding box in emerald green
                cv2.rectangle(annotated_img, (left, top), (right, bottom), (46, 204, 113), 3)
                label = f"{student_name} ({confidence}%)"
                cv2.putText(annotated_img, label, (left, max(top - 10, 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (46, 204, 113), 2, cv2.LINE_AA)
            else:
                # Unrecognized face in crimson red
                cv2.rectangle(annotated_img, (left, top), (right, bottom), (231, 76, 60), 2)
                cv2.putText(annotated_img, "Unregistered", (left, max(top - 10, 20)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (231, 76, 60), 2, cv2.LINE_AA)

        except Exception as e:
            print(f"Error matching face: {e}")

    return detected_student, all_students, len(encodings), annotated_img
