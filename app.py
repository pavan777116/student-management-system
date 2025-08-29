import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.utils import secure_filename

# --- App and Database Configuration ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_for_session_management'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

UPLOAD_FOLDER = 'static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

socketio = SocketIO(app)
db = SQLAlchemy(app)


# --- Database Models ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)


# UPDATED: Student model with new fields
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reg_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    stream = db.Column(db.String(50), default='B.Tech(CSE)')  # NEW FIELD
    sub_stream = db.Column(db.String(50), default='NA')  # NEW FIELD
    attendance = db.Column(db.Integer, default=0)  # NEW FIELD
    marks = db.Column(db.String(500), default='[]')  # Change to store JSON
    cgpa = db.Column(db.Float, default=0.0)
    profile_pic = db.Column(db.String(100), default='default_profile_pic.png')


# --- Create Database Tables and a default Admin user ---
with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username='admin').first():
        hashed_password = generate_password_hash('password', method='pbkdf2:sha256')
        default_admin = Admin(username='admin', password_hash=hashed_password)
        db.session.add(default_admin)
        db.session.commit()
        print("Default admin user created: username='admin', password='password'")

# --- Chat Message Storage ---
chat_history = {}


# --- Utility Functions ---
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# --- Main Routes ---
@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form['role']
        username = request.form['username']
        password = request.form['password']

        if role == 'admin':
            admin = Admin.query.filter_by(username=username).first()
            if admin and check_password_hash(admin.password_hash, password):
                session['logged_in_admin'] = True
                flash('Admin logged in successfully!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid admin credentials.', 'danger')
        else:
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password_hash, password):
                session['logged_in_student'] = True
                session['username'] = username
                flash('Logged in successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid student credentials.', 'danger')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        reg_no = request.form['reg_no']
        stream = request.form['stream']
        sub_stream = request.form.get('sub_stream', 'NA')  # Get sub-stream if available

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))
        if User.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('register'))
        if Student.query.filter_by(reg_no=reg_no).first():
            flash('Registration number already exists.', 'danger')
            return redirect(url_for('register'))

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password_hash=hashed_password)
        new_student = Student(
            reg_no=reg_no,
            name=username,
            stream=stream,
            sub_stream=sub_stream
        )

        try:
            db.session.add(new_user)
            db.session.add(new_student)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'An error occurred: {e}', 'danger')
    return render_template('register.html')


@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in_student'):
        flash('You need to be logged in to view this page.', 'warning')
        return redirect(url_for('login'))

    student = Student.query.filter_by(name=session['username']).first()
    if student:
        profile_pic_path = url_for('static', filename=f'profile_pics/{student.profile_pic}')
        # Safely parse marks from JSON string
        marks = json.loads(student.marks) if student.marks else []
        return render_template('dashboard.html', student=student, profile_pic_path=profile_pic_path, marks=marks)
    else:
        return render_template('dashboard.html', student=None)


@app.route('/upload_profile_pic', methods=['POST'])
def upload_profile_pic():
    if 'logged_in_student' not in session:
        flash('Please log in to upload a profile picture.', 'danger')
        return redirect(url_for('login'))

    student = Student.query.filter_by(name=session['username']).first()
    if 'profile_pic' not in request.files:
        flash('No file part', 'danger')
        return redirect(url_for('dashboard'))
    file = request.files['profile_pic']
    if file.filename == '':
        flash('No selected file', 'danger')
        return redirect(url_for('dashboard'))

    if file and allowed_file(file.filename):
        filename = secure_filename(f"{student.reg_no}_{file.filename}")
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        student.profile_pic = filename
        db.session.commit()
        flash('Profile picture uploaded successfully!', 'success')
    else:
        flash('Invalid file type. Allowed types: png, jpg, jpeg, gif', 'danger')

    return redirect(url_for('dashboard'))


@app.route('/logout')
def logout():
    session.pop('logged_in_student', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


# --- Admin Routes ---
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('logged_in_admin'):
        flash('You must be logged in as an admin to view this page.', 'warning')
        return redirect(url_for('login'))

    students_data = []
    students = Student.query.all()
    for student in students:
        marks = json.loads(student.marks) if student.marks else []
        student_dict = {
            'id': student.id,
            'reg_no': student.reg_no,
            'name': student.name,
            'stream': student.stream,
            'sub_stream': student.sub_stream,
            'attendance': student.attendance,
            'marks': marks,
            'cgpa': student.cgpa,
            'profile_pic_url': url_for('static', filename=f'profile_pics/{student.profile_pic}')
        }
        students_data.append(student_dict)

    return render_template('admin_dashboard.html', students=students_data)


@app.route('/edit_student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    if not session.get('logged_in_admin'):
        flash('You must be logged in as an admin.', 'warning')
        return redirect(url_for('login'))

    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        new_attendance = request.form['attendance']
        new_cgpa = request.form['cgpa']

        # Collect marks from the dynamic form
        marks_list = []
        for i in range(1, 7):  # 6 subjects
            subject_code = request.form.get(f'subject_code_{i}')
            score = request.form.get(f'score_{i}')
            if subject_code and score:
                marks_list.append({'code': subject_code, 'score': score})

        # Update the student's details
        student.attendance = new_attendance
        student.cgpa = new_cgpa
        student.marks = json.dumps(marks_list)

        db.session.commit()
        flash('Student details updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    # For GET request, pass existing data to the form
    existing_marks = json.loads(student.marks) if student.marks else []
    return render_template('edit_student.html', student=student, existing_marks=existing_marks)


@app.route('/admin_logout')
def admin_logout():
    session.pop('logged_in_admin', None)
    flash('Admin logged out successfully.', 'info')
    return redirect(url_for('login'))


# --- Private Chat Route & SocketIO Events ---
@app.route('/chat/<int:student_id>')
def chat(student_id):
    if session.get('logged_in_admin'):
        chat_partner = Student.query.get(student_id)
        if not chat_partner:
            flash('Student not found.', 'danger')
            return redirect(url_for('admin_dashboard'))
        user_role = 'Admin'
        user_name = 'Admin'
    elif session.get('logged_in_student'):
        chat_partner = Student.query.filter_by(name=session['username']).first()
        if chat_partner.id != student_id:
            flash('You can only chat with the admin.', 'danger')
            return redirect(url_for('dashboard'))
        user_role = 'Student'
        user_name = session['username']
    else:
        flash('You must be logged in to access chat.', 'warning')
        return redirect(url_for('login'))

    return render_template('chat.html', chat_partner=chat_partner, user_role=user_role, user_name=user_name)


@socketio.on('join_room')
def handle_join_room(data):
    room = data['room']
    join_room(room)
    if room not in chat_history:
        chat_history[room] = []

    emit('history', chat_history[room], room=request.sid)


@socketio.on('send_message')
def handle_send_message(data):
    room = data['room']
    message = data['message']
    sender = data['sender']

    chat_message = {'sender': sender, 'message': message}
    chat_history[room].append(chat_message)

    emit('new_message', chat_message, room=room)


# --- Running the App ---
if __name__ == '__main__':
    socketio.run(app, debug=True, allow_unsafe_werkzeug=True)