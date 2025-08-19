# Student Travels

A Django-based web application for managing student travel offers and bookings.

## Setup Instructions

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd student_travels
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   - Copy `.env.example` to `.env` and update values as needed.

5. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

6. **(Optional) Load demo data**
   ```bash
   python manage.py loaddata core/fixtures/demo_data.json
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the app**
   - Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Contributing

Feel free to submit issues or pull requests!
