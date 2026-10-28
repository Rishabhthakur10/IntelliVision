# 👁️ IntelliVision — Attendance System with AI

> **Python, Streamlit, Computer Vision, AI/ML | Completed**
> - **Automated Student Identification**: Developed an AI-based attendance system to automate student identification and attendance recording using 128-dimensional deep facial embeddings.
> - **Interactive Streamlit Web Application**: Built an interactive multi-role application using Python and Streamlit for instructor course administration and student attendance tracking.
> - **Computer Vision Recognition Engine**: Implemented AI and computer vision features (Dlib, OpenCV, Scikit-Learn SVM) to automate real-time face detection, recognition bounding boxes, and attendance marking.
> - **Tested & Refined**: Tested and refined the system to improve functionality, multi-face detection efficiency, and zero-configuration offline SQLite resilience.

---

## 🌟 Key Features

### 👨‍🏫 Instructor / Teacher Portal
- **Automated AI Face Attendance**: Stage single or multiple classroom photos or live camera captures. The AI scans and localizes all students, runs facial recognition, displays emerald green bounding box overlays with confidence scores, and automatically matches enrolled students.
- **Voice Biometric Roll-Call**: Optional acoustic speaker verification pipeline for sequential audio check-ins.
- **Course & Roster Management**: Create new courses (`CS101`, `AI204`), manage sections, track student enrollments, and generate instant QR Codes & shareable invite links.
- **Actionable Analytics & Reports**: View session summaries, total present vs absent metrics, and download audit-ready CSV attendance logs.

### 🎓 Student Portal
- **Instant FaceID Check-In**: Position face in front of the camera or upload a portrait for contactless verification.
- **Biometric Self-Enrollment**: New students can self-register their face vector in seconds with on-the-fly model re-training.
- **Attendance Rate Dashboard**: Track course-by-course attendance percentages, total classes conducted vs attended, and real-time attendance shortage warnings (< 75% alert).
- **Fast Course Joining**: Join courses with a single click using instructor course codes or QR links.

### 🌐 Marketing & Demo Landing Page
- Modern, animated responsive landing page built with Flask, CSS3, and dynamic SVG illustrations detailing the teacher & student workflows and system architecture.

---

## 🛠️ System Architecture & Tech Stack

```
IntelliVision/
├── app.py                      # Main Streamlit application
├── landing_page/               # Flask marketing & demo landing page
│   ├── app.py
│   ├── templates/index.html
│   └── static/ (css, js, img)
├── src/
│   ├── components/             # Reusable UI cards, headers, footers & modals
│   │   ├── header.py
│   │   ├── footer.py
│   │   ├── subject_card.py
│   │   ├── dialog_add_photo.py
│   │   ├── dialog_attendance_results.py
│   │   ├── dialog_create_subject.py
│   │   ├── dialog_enroll.py
│   │   ├── dialog_auto_enroll.py
│   │   ├── dialog_share_subject.py
│   │   └── dialog_voice_attendance.py
│   ├── database/               # Hybrid persistence layer (SQLite + Supabase)
│   │   ├── config.py
│   │   └── db.py
│   ├── pipelines/              # Computer Vision & Audio AI models
│   │   ├── face_pipeline.py    # Dlib + OpenCV + Scikit-Learn SVM
│   │   └── voice_pipeline.py   # Resemblyzer + Librosa
│   ├── screens/                # Role-based interfaces
│   │   ├── home_screen.py
│   │   ├── teacher_screen.py
│   │   └── student_screen.py
│   └── ui/                     # Global styling and CSS themes
│       └── base_layout.py
├── intellivision.db            # Auto-generated SQLite database
├── start.py                    # Multi-process orchestrator
├── run.sh                      # Shell launch script
└── requirement.txt             # Python dependencies
```

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **Frontend Framework** | Streamlit 1.65+ | Reactive, high-productivity dashboards |
| **Landing Page** | Flask, HTML5, CSS3 | Product showcase and workflow tour |
| **Vision AI** | Dlib, OpenCV, Scikit-Learn | Face localization & 128-D vector classification |
| **Persistence** | SQLite / Supabase | Relational data storage & biometric vectors |
| **Utilities** | Pandas, Segno, Bcrypt | Analytics, QR code generation, password hashing |

---

## 🚀 Quickstart Guide

### 1. Activate Environment
The project comes with a pre-configured Python virtual environment:
```bash
cd /Users/rishabhthakur/Desktop/IntelliVision
source .venv/bin/activate
```

### 2. Run the Application
You can launch the Streamlit App, the Landing Page, or both using the convenience script:

```bash
# Option A: Run the main Streamlit Attendance App (Port 8501)
./run.sh
# or
streamlit run app.py

# Option B: Run the Landing Page (Port 5002)
./run.sh landing

# Option C: Run Both concurrently
python start.py both
```

### 3. Demo Credentials
The system automatically creates initial mock courses and users on first run:
- **Instructor Login**:
  - Username: `prof.sharma`
  - Password: `teacher123`
- **Secondary Instructor**:
  - Username: `admin`
  - Password: `admin123`
- **Pre-Enrolled Students**:
  - `Aarav Mehta`, `Ananya Sharma`, `Rohan Verma`, `Priya Patel`, `Kabir Singh`

---

## 🧪 Testing & Verification
The system has been tested across:
1. **Face Localization & Extraction**: Tested on single portrait captures and multi-person classroom scenes.
2. **Model Training & Inference**: Evaluated SVM decision boundaries against Euclidean distance thresholds (`resemblance_threshold = 0.60`).
3. **Database Transactions**: Tested concurrent enrollment, logging, and CSV summary generation on local SQLite.
