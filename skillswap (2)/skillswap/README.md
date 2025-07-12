# SkillSwap Platform - Hackathon Project

This is a mini-application that enables users to list their skills and request to swap them with other users. The platform features an AI-powered matchmaking system to intelligently suggest swap partners.

This project was built as part of a 5-hour hackathon.

## Features

- **User Authentication:** Sign up, log in, log out.
- **Profile Management:** Users can create and edit their profiles, adding:
  - Location and availability.
  - A list of skills they offer.
  - A list of skills they want.
- **AI Skill Suggester:** Gemini AI helps users find professional names for their skills.
- **User Browsing & Search:** Search for other users based on the skills they offer.
- **Swapping System:**
  - Send, accept, and reject skill swap requests.
  - A dashboard to manage all pending and active swaps.
- **AI Matchmaker:** A core feature that uses Gemini AI to analyze all users and provide intelligent, contextual swap recommendations.
- **Admin Panel:** A built-in Django admin interface to manage users, skills, and swaps.

---

## Tech Stack

- **Backend:** Django
- **Frontend:** Bootstrap 5 (with a dark/light theme switcher)
- **Database:** SQLite (default for Django)
- **AI:** Google Gemini API

---

## Setup and Installation

Follow these steps to get the project running on your local machine.

### 1. Prerequisites

- Python 3.8 or higher
- `pip` (Python package installer)
- `venv` (for creating virtual environments)

### 2. Clone the Repository

First, clone this repository to your local machine (or simply download the source code zip).

```bash
git clone <your-repository-url>
cd skillswap-project-folder





# Create the virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate




pip install -r requirements.txt


5. Configure the Gemini API Key
This project requires a Google Gemini API key to power its AI features.
Get your API key from Google AI Studio.
Open the settings file: skillswap_project/settings.py.
Find the line at the bottom of the file that says GEMINI_API_KEY = "YOUR_API_KEY_HERE" and replace "YOUR_API_KEY_HERE" with your actual key.

# In skillswap_project/settings.py
GEMINI_API_KEY = "ai-key-goes-here-xxxxxxxx"


6. Set Up the Database
Run the database migrations to create the necessary tables in the SQLite database.
Generated bash

python manage.py makemigrations
python manage.py migrate



7. Create a Superuser
To access the admin panel, you need to create an admin account.

python manage.py createsuperuser


8. Run the Development Server
You're all set! Start the Django development server.

python manage.py runserver



How to Use the Application
Sign Up: Go to http://127.0.0.1:8000/signup/ to create a new user account.
Edit Your Profile: After signing up, you'll be taken to your profile page. Add some skills you offer and some you want.
Explore:
Browse Swaps: Manually search for other users.
AI Matcher: Use the AI to find the best potential swap partners for you!
Dashboard: Manage your incoming and outgoing swap requests.
Admin Panel: Visit http://127.0.0.1:8000/admin/ and log in with your superuser account to manage all application data.