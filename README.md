# Instagram Clone

A full-featured Instagram-like social media web application built with Django.  
Users can register, post images, follow others, send messages, view stories, receive notifications, and more.

---

## Features

- User registration, login, and password reset
- Profile editing, privacy settings, and account deactivation
- Follow/unfollow users, follow requests for private accounts
- Post creation, editing, deletion, and commenting
- Instagram-style stories with viewers tracking
- Direct messaging (DMs) with read receipts
- Notifications for likes, comments, follows, and requests
- Block/unblock users
- Responsive, modern UI with Bootstrap

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/ahmedosamax/instagram-clone.git
cd instagram-clone/InstagramClone
```

### 2. Apply Migrations

```bash
python manage.py migrate
```

### 3. Create a Superuser (Admin)

```bash
python manage.py createsuperuser
```

### 4. Run the Development Server

```bash
python manage.py runserver
```

### 5. Access the App

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Usage Guidelines

- **Register** for a new account or **log in** with existing credentials.
- **Edit your profile** and set it to private if you want to approve followers.
- **Create posts** with images and captions.
- **View and create stories** (visible for 24 hours).
- **Follow** other users, send follow requests to private accounts.
- **Send and receive messages** in the inbox.
- **Receive notifications** for likes, comments, follows, and requests.
- **Block or unblock** users from their profile page.
- **Deactivate or delete** your account from your profile settings.
- **Reset your password** via the "Forgot password?" link on the login page.

---

## Project Architecture

```
InstagramClone/
│
├── InstagramClone/           # Django project settings and root URLs
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── users/                    # User management: registration, login, profile, follow, block
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/users/
│
├── posts/                    # Posts, comments, likes
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/posts/
│
├── stories/                  # Instagram-style stories
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/stories/
│
├── messages_app/             # Direct messaging (DMs)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/messages_app/
│
├── notifications/            # Notifications system
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/notifications/
│
├── static/                   # Static files (CSS, JS, images)
│
├── templates/                # Base templates (base.html)
│
└── manage.py                 # Django management script
```

---

## Email & Password Reset

- By default, password reset emails are printed to the console.
- To enable real email sending, configure `EMAIL_BACKEND` and SMTP settings in `settings.py`.

---

## Tech Stack

- Django (Backend)
- HTML, CSS, Bootstrap (Frontend)
- SQLite (Default DB)
- JavaScript (Dynamic interactions)


**Enjoy your Instagram Clone!**