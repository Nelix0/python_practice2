from flask import Flask, request, redirect, render_template_string, send_file
import sqlite3
import datetime
from fpdf import FPDF

app = Flask(__name__)
DB_PATH = "attendance.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            time TEXT,
            action TEXT
        )
    ''')
    conn.commit()
    conn.close()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        action = request.form["action"]
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO attendance (name, time, action) VALUES (?, ?, ?)", (name, now, action))
        conn.commit()
        conn.close()
        return redirect("/")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM attendance ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    return render_template_string("""
    <h2>Учёт рабочего времени</h2>
    <form method="post">
        Имя: <input type="text" name="name" required>
        <select name="action">
            <option value="Приход">Приход</option>
            <option value="Уход">Уход</option>
        </select>
        <input type="submit" value="Отправить">
    </form>
    <a href="/download"> Скачать отчёт (PDF)</a>
    <hr>
    <table border="1">
        <tr><th>ID</th><th>Имя</th><th>Время</th><th>Действие</th></tr>
        {% for row in rows %}
        <tr><td>{{ row[0] }}</td><td>{{ row[1] }}</td><td>{{ row[2] }}</td><td>{{ row[3] }}</td></tr>
        {% endfor %}
    </table>
    """, rows=rows)

@app.route("/download")
def download_pdf():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM attendance ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    pdf = FPDF()
    pdf.add_page()

    
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", "", 12)
    pdf.cell(200, 10, txt="Отчёт по учёту рабочего времени", ln=1, align="C")
    pdf.ln(5)

    pdf.set_font("DejaVu", "", 10)
    for row in rows:
        pdf.cell(0, 10, f"ID: {row[0]}, Имя: {row[1]}, Время: {row[2]}, Действие: {row[3]}", ln=1)

    pdf_path = "report.pdf"
    pdf.output(pdf_path)
    return send_file(pdf_path, as_attachment=True)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)