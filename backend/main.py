from flask import Flask, request, jsonify, send_file, session
import pandas as pd
from functools import wraps
from utils import (
    generate_seating_arrangement,
    generate_room_seating_pdf,
    generate_hall_ticket_pdf,
    generate_all_hall_tickets_zip
)
from io import BytesIO
from flask import send_file
import re

app = Flask(__name__)
app.secret_key = "super_secret_key"

rooms_df = None
timetable_df = None
allocation_df = None


# ------------------- AUTH HELPERS -------------------
def categorize_email(email):
    if email.endswith('@cbit.ac.in'):
        return 'faculty'
    elif email.endswith('@cbit.org.in'):
        return 'student'
    else:
        return 'invalid'


def faculty_only(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'role' not in session or session['role'] != 'faculty':
            return jsonify({"error": "Invalid credentials"}), 403
        return func(*args, **kwargs)
    return wrapper


# ------------------- ROUTES -------------------

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    if not email:
        return jsonify({"error": "Email required"}), 400

    if categorize_email(email) != 'faculty':
        return jsonify({"error": "Access denied. Only faculty can log in."}), 403

    session['email'] = email
    session['role'] = 'faculty'
    return jsonify({"message": "Login successful"}), 200


@app.route('/upload_rooms', methods=['POST'])
@faculty_only
def upload_rooms():
    global rooms_df
    if 'file' not in request.files:
        return jsonify({"error": "rooms.csv file required"}), 400
    file = request.files['file']
    rooms_df = pd.read_csv(file)
    rooms_df.columns = [c.strip().replace(" ", "") for c in rooms_df.columns]
    return jsonify({"message": "Rooms uploaded successfully"}), 200


@app.route('/upload_timetable', methods=['POST'])
@faculty_only
def upload_timetable():
    global timetable_df
    if 'file' not in request.files:
        return jsonify({"error": "timetable.csv file required"}), 400
    file = request.files['file']
    timetable_df = pd.read_csv(file)
    timetable_df.columns = [c.strip().replace(" ", "") for c in timetable_df.columns]
    return jsonify({"message": "Timetable uploaded successfully"}), 200


@app.route('/generate_room_seating_pdf', methods=['GET'])
@faculty_only
def generate_room_pdf():
    global allocation_df
    if timetable_df is None or rooms_df is None:
        return jsonify({"error": "Please upload both timetable and rooms CSV first"}), 400

    allocation_df = generate_seating_arrangement(timetable_df, rooms_df)
    exam_meta = {
        "ExamDate": allocation_df.iloc[0]["ExamDate"],
        "ExamSession": allocation_df.iloc[0]["ExamSession"]
    }
    pdf_bytes = generate_room_seating_pdf(allocation_df, exam_meta)
    return send_file(pdf_bytes, mimetype='application/pdf', as_attachment=True, download_name='RoomSeating.pdf')


@app.route('/generate_hall_ticket/<roll_no>', methods=['GET'])
@faculty_only
def generate_hall_ticket(roll_no):
    global allocation_df
    if allocation_df is None or allocation_df.empty:
        return jsonify({"error": "Seating not generated yet"}), 400

    student = allocation_df[allocation_df["RollNo"].astype(str) == str(roll_no)]
    if student.empty:
        return jsonify({"error": f"No record found for Roll No {roll_no}"}), 404


    pdf_bytes = generate_hall_ticket_pdf(student.iloc[0])

    # Wrap in BytesIO for Flask
    pdf_buffer = BytesIO(pdf_bytes)
    pdf_buffer.seek(0)


    roll_no_safe = re.sub(r'[^A-Za-z0-9_-]', '', str(student['RollNo']))
    download_name = f"hall_ticket_{roll_no_safe}.pdf"

    return send_file(
    pdf_buffer,
    mimetype='application/pdf',
    download_name=download_name
    )


@app.route('/download_all_halltickets', methods=['GET'])
def download_all_halltickets():
    global allocation_df
    if allocation_df is None:
        return jsonify({"error": "Seating not generated yet"}), 400

    zip_bytes = generate_all_hall_tickets_zip(allocation_df)
    return send_file(
        zip_bytes,
        mimetype='application/zip',
        download_name='all_hall_tickets.zip'
    )


@app.route('/logout', methods=['POST'])
@faculty_only
def logout():
    session.clear()
    return jsonify({"message": "Logged out successfully"}), 200


# ------------------- RUN APP -------------------
if __name__ == '__main__':
    app.run(debug=True)
