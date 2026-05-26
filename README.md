# Kitchen Service

Django-based web application for managing a kitchen service, cooks, dishes, and ingredients in a restaurant. This project was developed as part of the Mate Academy Python Developer Course.

## Check it out!

[Kitchen Service project deployed to Render](https://[xxx].render.com/)

## Installation

Python3 must be already installed.

Repository URL: [https://github.com/Sacchar20/kitchen-service](https://github.com/Sacchar20/kitchen-service)

```shell
git clone https://github.com/Sacchar20/kitchen-service.git
cd kitchen-service
python3 -m venv .venv
source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver


Features
Custom User Model — Implemented custom Cook model with authentication and years of experience validation.

Full CRUD Operations — Management for Dishes, Dish Types, and Cooks directly from the website interface.

Access Control — Secure views with authorization requirements preventing unauthorized actions.

Clean UI — Responsive interface built with Bootstrap 5, customized for better user experience.

Admin Panel — Powerful built-in Django admin dashboard for advanced data management.
