# **Healthcare Backend**

A backend service built with **Django** and **Django REST Framework** to manage appointments for the healthcare project.

---

## **Features**
- RESTful API for managing appointments.
- Admin panel for creating, reading, updating, and deleting appointments.
- API endpoints for CRUD operations.

---

## **Setup Instructions**

### **1. Clone the Repository**
```bash
git clone <repository-url>
cd healthcare-backend
```

### **2. Set Up a Virtual Environment**
```bash
python -m venv venv
source venv/bin/activate  # For Windows: venv\Scripts\activate
```
### **3. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **4. Apply Database Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **5. Create a Superuser**
```bash
python manage.py createsuperuser
```
Follow the prompts to set up a username, email, and password.

### **6. Start the Development Server**
```bash
python manage.py runserver
```
The server will start at: http://127.0.0.1:8000/

## **API Endpoints**

### **Base URL**: `http://127.0.0.1:8000/appointments/`

### **1. Retrieve All Appointments**
```http
GET /appointments/ #
```
**Description:** Fetch a list of all saved appointments.

**Response:**
```json
[
    {
        "id": 1,
        "title": "Doctor's Appointment",
        "description": "Annual check-up",
        "date_time": "2025-01-15T10:00:00Z",
        "created_at": "2025-01-10T20:58:03.192615Z",
        "updated_at": "2025-01-10T20:58:03.192615Z"
    }
]
```
### **2. Create a New Appointment**
```http
POST /appointments/
```

**Description:** Add a new appointment.

**Request Body:**
```json
{
    "title": "Doctor's Appointment",
    "description": "Annual check-up",
    "date_time": "2025-01-15T10:00:00Z"
}
```
**Response:**
```json
{
    "id": 1,
    "title": "Doctor's Appointment",
    "description": "Annual check-up",
    "date_time": "2025-01-15T10:00:00Z",
    "created_at": "2025-01-10T20:58:03.192615Z",
    "updated_at": "2025-01-10T20:58:03.192615Z"
}
```