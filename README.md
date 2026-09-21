# hospital-management-system
This app has two parts:

Backend — Flask REST API (Python) with JWT authentication, SQLite database, Redis caching, and Celery for background jobs (emails, reports, CSV export).
Frontend — Vue 3 single-page application with role-based dashboards for Admin, Doctor, and Patient.


✨ Features
👑 Admin
Dashboard with key stats (doctors, patients, appointments, pending verifications)
Add / edit / verify / remove doctors
View / edit / remove patients
Manage departments (add / edit / delete)
View all appointments, cancel appointments
Manage doctor availability schedules

🩺 Doctor
Dashboard with today's & this week's appointments
View and filter appointments (all / today / week)
Mark appointments as completed with diagnosis & prescription
Reschedule or cancel appointments
Manage own availability slots
View patient list and full treatment history
Edit profile (contact, address, email, bio)

🧑 Patient
Register and log in
Dashboard with upcoming & recent appointments
Browse verified doctors, filter by name/department
Book, reschedule, or cancel appointments based on doctor availability
View full treatment history
Export treatment history as CSV (background job) and download it
Edit profile

Background Jobs (Celery)
Daily email reminders for patients with appointments that day
Monthly activity report emailed to each doctor
Async CSV export of a patient's treatment history

**Technologies Used**
Layer	Technology
Frontend	                    Vue 3, Vue Router, Axios
Backend	                     Flask, Flask-SQLAlchemy, Flask-Caching, Flask-CORS
Auth	                        JWT (PyJWT)
Database	                    SQLite
Cache/Queue	                 Redis
Background                   Jobs	Celery
Styling                      CSS


**Architecture Overview:** 
Hospital_management_app/
│
├── backend/
│   ├── app.py              # Flask app entry point
│   ├── config.py           # App configuration
│   ├── models.py           # SQLAlchemy models
│   ├── extensions.py       # Cache instance
│   ├── auth_utils.py       # JWT + role-based decorators
│   ├── tasks.py            # Celery tasks (emails, reports, CSV export)
│   ├── requirements.txt
│   └── routes/
│       ├── auth_routes.py
│       ├── admin_routes.py
│       ├── doctor_routes.py
│       └── patient_routes.py
│
└── frontend/
    ├── package.json
    ├── babel.config.js
    ├── vue.config.js
    ├── public/
    │   └── index.html
    └── src/
        ├── main.js
        ├── App.vue
        ├── api.js               # Axios instance + interceptors
        ├── router/index.js      # Routes + auth guards
        ├── components/Layout.vue
        └── views/
            ├── Login.vue
            ├── Register.vue
            ├── admin/    (Dashboard, Doctors, Patients, Appointments, Departments)
            ├── doctor/   (Dashboard, Appointments, Patients, Schedule, Profile)
            └── patient/  (Dashboard, Doctors, Appointments, History, Profile)
 







