# HTF25-Team-116

# 🧠 Examzy - Automated Exam Seating Planner

**Examzy** is a full-stack application designed to automate the complex and time-consuming task of exam seating arrangement. It provides a backend API for processing data and generating all necessary documents, along with a visual frontend prototype for an intuitive faculty-facing user interface.

## Problem Statement

The Automated Exam Seating Planner simplifies and streamlines the complex task of organizing exam seating arrangements in colleges and universities. It automates the generation of seating charts based on inputs like student lists, roll numbers, subject codes, and classroom capacities, ensuring fair distribution of students across rooms. The system includes features such as randomized seat allocation to minimize malpractice, support for multiple exam sessions, and instant conflict detection for overlapping exams. It also produces printable seating charts, room-wise allotments, and individual hall tickets for easy distribution.

## Proposed Solution

**Examzy** is a user-friendly and secure portal for faculty and administrators. After signing in, users are brought to a central dashboard that provides direct access to the three most critical exam management tasks. From this single screen, faculty can instantly **generate a new seating plan**, **download student hall tickets** for a specific exam, or quickly **check their own invigilation assignments**. This design streamlines the entire process, organizing all essential tools into one simple and efficient command center.

## 🚀 Features

### Backend (API)
* **Smart Seat Allocation:** Randomizes student lists and separates them by roll number prefixes to minimize malpractice.
* **PDF Room Charts:** Dynamically generates PDF files for each exam room, showing the seat-by-seat student allotment.
* **QR-Coded Hall Tickets:** Generates individual PDF hall tickets for each student, complete with a unique QR code for verification.
* **Bulk Download:** Creates a single `.zip` file containing all generated hall tickets for easy distribution.
* **Secure:** Includes a basic, extendable authentication system for faculty-only access.

### Frontend (UI Prototype)
* **Secure Faculty Login:** A dedicated login page with client-side validation.
* **Centralized Dashboard:** A main hub providing access to all core functions in a clean, card-based layout.
* **Seating Plan Generator:** A simple page for an administrator to upload a single consolidated data file.
* **Hall Ticket Downloader:** A tool on the dashboard to simulate downloading hall tickets, filterable by exam and branch.
* **Invigilation Check:** A utility for faculty to quickly check their assigned invigilation room.

---

## 🧩 Tech Stack

| Component | Technology / Library | Purpose |
| :--- | :--- | :--- |
| **Frontend** | HTML5 | Provides the structure for the login, dashboard, and generator pages. |
| **Frontend** | CSS3 | Used for all styling, layout (Flexbox/Grid), animations, and the colorful UI. |
| **Frontend** | JavaScript | Powers client-side interactivity, form validation, and dynamic messages. |
| **Frontend Service**| Google Fonts | Imports the 'Poppins' font to ensure a modern and consistent typography. |
| **Backend Framework** | Flask | Creates the web server, API routes (`/login`, `/upload`), and handles requests. |
| **Data Handling** | Pandas | Reads, processes, and manipulates the uploaded CSV/Excel data. |
| **PDF Generation** | FPDF (pyfpdf) | Dynamically generates PDF documents for hall tickets and room charts. |
| **QR Code Generation**| qrcode | Creates unique QR codes for embedding in the student hall tickets. |
| **File Handling** | ZipFile | Packages all generated hall tickets into a single downloadable ZIP archive. |
| **Core Language** | Python | The primary language used for all backend logic and data processing. |

---

## 📁 File Structure

├── backend/
│   ├── main.py         # Flask server, API routes
│   └── util.py         # Core logic for PDF/QR/ZIP generation
│
├── frontend/
│   ├── login.html      # The main login/authentication page
│   └── generator.html  # The page to upload data and receive the output
│
└── README.md           # This file

---

## ⚙️ How to Run

This project has two parts (backend and frontend) that are run separately.


### 2. Frontend (UI Prototype)

1.  **Navigate to the frontend folder:**
    ```bash
    cd frontend
    ```
2.  **Open the files in your browser:**
    * Open `login.html` to see the login page.
    * Open `dashboard.html` to see the main dashboard.
    * Open `generator.html` to see the file upload page.

**Note:** The frontend files are a **prototype** and are not yet connected to the
