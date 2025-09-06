Student Management System
This is a comprehensive web application designed to manage student and academic information. The system features separate dashboards for students and administrators, with functionalities for registration, data management, and even a private chat system.

The project is built using Python with the Flask framework, and it utilizes SQLAlchemy for database management and Socket.IO for real-time communication.

🚀 Features
This application offers a dual-role system with distinct features for students and admins.

Student Portal
User-friendly Dashboard: Students can log in to view their academic details, including attendance, marks, and CGPA.

Profile Management: Users can upload a custom profile picture.

Real-time Chat: Students can initiate a private chat with the administrator for any queries or support.

Admin Portal
Secure Login: A dedicated admin login to access and manage student data.

Student Data Management: View, add, and edit details for all students, including name, registration number, stream, attendance, and marks.

Attendance and Marks Tracking: Admins can easily update student attendance and marks for individual subjects.

CGPA Calculation: A field to manage and update a student's CGPA.

Private Chat: Admins can view and respond to messages from individual students in real-time.

🛠️ Technologies Used
Backend: Python, Flask

Database: SQLAlchemy (using SQLite for development)

Real-time Communication: Flask-SocketIO

Frontend: HTML, CSS, JavaScript (used for real-time chat)

User Authentication: Werkzeug Security (generate_password_hash, check_password_hash)

📦 How to Run the Project Locally
Follow these simple steps to set up and run the project on your local machine.

Prerequisites
Python 3.x

pip (Python package installer)

Step 1: Clone the Repository
Clone this repository to your local machine using git.

Bash

git clone https://github.com/pavan777116/student-management-system.git
cd student-management-system
Step 2: Create a Virtual Environment
It's a best practice to use a virtual environment to manage dependencies.

Bash

python -m venv venv
Activate the virtual environment:

On Windows:

Bash

.\venv\Scripts\activate
On macOS and Linux:

Bash

source venv/bin/activate
Step 3: Install Dependencies
Install all the required Python packages from the requirements.txt file (you will need to create this if it's not in your repository).

Bash

pip install -r requirements.txt
Note: The required packages are Flask, Flask-SQLAlchemy, Flask-SocketIO, Werkzeug, python-dotenv (or similar), and sqlalchemy.

Step 4: Run the Application
The application will automatically create a default admin user and the database file (site.db) upon its first run.

Bash

python app.py
Step 5: Access the Application
Open your web browser and navigate to:

http://127.0.0.1:5000/
You will be redirected to the login page.

🔑 Default Credentials
The system automatically creates a default administrator account for easy setup.

Admin Username: admin

Admin Password: password

You can log in with these credentials to access the admin dashboard and start adding new student records.

📄 File Structure
student-management-system/
├── app.py                      # The main application file
├── static/                     # Static files (CSS, JS, images)
│   ├── profile_pics/           # Folder to store uploaded profile pictures
│   └── (other static files)
├── templates/                  # HTML templates
│   ├── admin_dashboard.html
│   ├── chat.html
│   ├── dashboard.html
│   ├── edit_student.html
│   ├── login.html
│   └── register.html
├── site.db                     # Database file (will be created automatically)
└── README.md
👥 Contribution
Feel free to fork this repository and contribute. You can help by:
  Improving the UI/UX.
  Adding new features (e.g., automated CGPA calculation, new user roles).
  Fixing bugs or security vulnerabilities.
