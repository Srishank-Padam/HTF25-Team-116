import pandas as pd
import random
import qrcode
from io import BytesIO
from fpdf import FPDF
import zipfile
import io
import os
import tempfile


# ----------------------------------------------------------
# Helper for separating roll prefixes to avoid adjacency
# ----------------------------------------------------------
def _separate_adjacent_prefixes(roll_list):
    prefix_map = {}
    for roll in roll_list:
        prefix = ''.join(filter(str.isalpha, str(roll)))
        prefix_map.setdefault(prefix, []).append(roll)

    for prefix in prefix_map:
        random.shuffle(prefix_map[prefix])

    separated = []
    while any(prefix_map.values()):
        for prefix, rolls in list(prefix_map.items()):
            if rolls:
                separated.append(rolls.pop())
    return separated


# ----------------------------------------------------------
# Seat allocation logic with randomization + prefix handling
# ----------------------------------------------------------
def generate_seating_arrangement(timetable_df, rooms_df):
    if timetable_df is None or rooms_df is None:
        raise ValueError("Timetable or Rooms data not provided")

    timetable_df = timetable_df.copy()
    timetable_df["RollNo"] = timetable_df["RollNo"].astype(str).str.strip()
    timetable_df["RoomNo"] = timetable_df["RoomNo"].astype(str).str.strip()

    seating_records = []
    grouped = timetable_df.groupby(["ExamDate", "ExamSession"])

    for (exam_date, exam_session), group in grouped:
        room_list = list(rooms_df["RoomNo"])
        room_capacities = dict(zip(rooms_df["RoomNo"], rooms_df["Capacity"]))
        students = group.sample(frac=1).reset_index(drop=True)

        roll_numbers = _separate_adjacent_prefixes(students["RollNo"].tolist())

        student_idx = 0
        for room_no in room_list:
            capacity = int(room_capacities[room_no])
            for seat_no in range(1, capacity + 1):
                if student_idx >= len(roll_numbers):
                    break
                roll = roll_numbers[student_idx]
                student = students[students["RollNo"] == roll].iloc[0]
                seating_records.append({
                    "RollNo": student["RollNo"],
                    "StudentName": student["StudentName"],
                    "Department": student["Department"],
                    "Subject": student["Subject"],
                    "ExamDate": student["ExamDate"],
                    "ExamSession": student["ExamSession"],
                    "RoomNo": room_no,
                    "SeatNo": seat_no
                })
                student_idx += 1

    allocation_df = pd.DataFrame(seating_records)
    return allocation_df


# ----------------------------------------------------------
# Room Seating PDF Generator
# ----------------------------------------------------------

def generate_room_seating_pdf(allocation_df, exam_meta=None):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for room_no, room_group in allocation_df.groupby("RoomNo"):
        pdf.add_page()

        # --- HEADER ---
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, f"Room Seating Arrangement - {room_no}", ln=True, align="C")

        pdf.set_font("Arial", "I", 12)
        if exam_meta:
            pdf.cell(0, 8, f"Exam Date: {exam_meta.get('ExamDate', '')} | Session: {exam_meta.get('ExamSession', '')}", ln=True, align="C")
        pdf.ln(5)

        # --- TABLE HEADER ---
        pdf.set_font("Arial", "B", 11)
        col_widths = [20, 35, 50, 35, 50]  # Adjust widths as needed
        headers = ["Seat No", "Roll No", "Student Name", "Department", "Subject"]

        for i, header in enumerate(headers):
            pdf.cell(col_widths[i], 10, header, border=1, align="C")
        pdf.ln()

        # --- TABLE ROWS ---
        pdf.set_font("Arial", "", 10)
        for _, row in room_group.iterrows():
            pdf.cell(col_widths[0], 8, str(row["SeatNo"]), border=1, align="C")
            pdf.cell(col_widths[1], 8, str(row["RollNo"]), border=1, align="C")
            pdf.cell(col_widths[2], 8, str(row["StudentName"]), border=1)
            pdf.cell(col_widths[3], 8, str(row["Department"]), border=1)
            pdf.cell(col_widths[4], 8, str(row["Subject"]), border=1)
            pdf.ln()

        pdf.ln(5)

    # Return PDF as BytesIO
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    bio = BytesIO(pdf_bytes)
    bio.seek(0)
    return bio


# ----------------------------------------------------------
# Hall Ticket Generator for Single Student
# ----------------------------------------------------------
def generate_hall_ticket_pdf(student):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # --- TITLE ---
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, "Exam Hall Ticket", ln=True, align="C")
    pdf.ln(8)

    # --- QR CODE ---
    qr_data = f"{student['RollNo']} - {student['StudentName']} - {student['Subject']} - {student['ExamDate']} - {student['RoomNo']}"
    qr_img = qrcode.make(qr_data)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_qr:
        qr_img.save(tmp_qr.name)
        tmp_path = tmp_qr.name

    # --- STUDENT DETAILS TABLE ---
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, "Student Details", ln=True)
    pdf.set_font("Arial", "", 11)

    line_height = 10
    col1_width = 45
    col2_width = 120

    details = [
        ("Name", student["StudentName"]),
        ("Roll No", student["RollNo"]),
        ("Department", student["Department"]),
        ("Subject", student["Subject"]),
        ("Exam Date", student["ExamDate"]),
        ("Exam Session", student["ExamSession"]),
        ("Room No", student["RoomNo"])
    ]

    x_start = pdf.get_x()
    y_start = pdf.get_y()

    # Draw table with borders
    for key, value in details:
        pdf.cell(col1_width, line_height, key, border=1)
        pdf.cell(col2_width, line_height, str(value), border=1, ln=True)

    # Add QR code aligned to top right
    pdf.image(tmp_path, x=165, y=y_start, w=30, h=30)
    os.remove(tmp_path)

    # --- FOOTER ---
    pdf.ln(10)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 10, "Please bring this hall ticket and a valid ID card to the exam hall.", ln=True, align="C")

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes


def generate_all_hall_tickets_zip(allocation_df):
    """
    Generate a ZIP of all hall ticket PDFs.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        for _, student in allocation_df.iterrows():
            pdf_bytes = generate_hall_ticket_pdf(student)  # returns BytesIO or bytes
            roll_no_safe = str(student['RollNo']).strip().replace(' ', '_')
            filename = f"hall_ticket_{roll_no_safe}.pdf"
            
            # If pdf_bytes is BytesIO, use getvalue()
            if isinstance(pdf_bytes, BytesIO):
                zipf.writestr(filename, pdf_bytes.getvalue())
            else:
                zipf.writestr(filename, pdf_bytes)

    zip_buffer.seek(0)
    return zip_buffer
