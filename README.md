# **Healthcare Backend**

A backend service built with **Django** and **Django REST Framework** to manage appointments for the healthcare project.

---

## **Features**
- RESTful API for managing appointments.
- Admin panel for creating, reading, updating, and deleting appointments.
- API endpoints for CRUD operations.
- Authentication for secure access.
- Support for PostgreSQL in production.

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

### **4. Configure Enviornment Variables**
Create a .env file in the root directory and set the following variables:
```bash
SECRET_KEY=your_secret_key
DEBUG=True  # Set to False in production
DATABASE_URL=sqlite:///db.sqlite3  # Use PostgreSQL in production
```

### **5. Apply Database Migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

### **6. Create a Superuser**
```bash
python manage.py createsuperuser
```
Follow the prompts to set up a username, email, and password.

### **7. Start the Development Server**
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
### **3. Retrieve a Single Appointment**
```http
GET /appointments/{id}/
```
**Description:** Fetch details of a single appointment by ID.

### **4. Update an Appointment**
```http
PUT /appointments/{id}/
```
**Description:** Update an appointment by ID.
**Request Body:**
```{
    "title": "Updated Appointment",
    "description": "Updated description",
    "date_time": "2025-01-20T15:00:00Z"
}
```
### **5. Delete an Appointment**
```http
DELETE /appointments/{id}/
```
**Description:** Delete an appointment by ID.

## **Admin Panel**

- **URL**: `http://127.0.0.1:8000/admin/`
- **Credentials**: Use the superuser account created earlier.
- **Features**: Manage appointments (create, edit, delete) via the admin interface.

## **Testing**

### **Run Tests**

To run test, execute the following command:
```
python manage.py test
```

## **Technologies Used**

- **Django**: Python web framework.
- **Django REST Framework**: For building REST APIs.
- **SQLite**: Default database for local development.

## **Deployment**

### **1. Prepare for Deployment**
- Set DEBUG=False in the .env file..
- Use a production-ready database like PostgreSQL.
- Configure a web server like Gunicorn or uWSGI.
