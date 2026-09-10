# XCommerce

XCommerce is a full-stack e-commerce web application developed with
Python and Django. It provides product browsing, customer authentication,
shopping cart, wishlist, checkout, order management, product reviews,
personalized recommendations, and an administrative dashboard.

## Project Purpose

The purpose of this project is to develop and evaluate a secure,
responsive, and user-friendly e-commerce web application using Django.

This project demonstrates full-stack web development, database design,
authentication, authorization, testing, security, and responsive UI design.

## Main Features

### Customer Features

- Customer registration, login, and logout
- Customer profile and profile image
- Product search
- Category filtering
- Product detail pages
- Shopping cart
- Quantity update and product removal
- Wishlist
- Checkout and shipping information
- Order confirmation
- Order history
- Product reviews and 1–5 star ratings
- Personalized product recommendations
- Responsive design for desktop and mobile

### Administrator Features

- Secure Django administration
- Product and category management
- Customer management
- Order and order-status management
- Review management
- Wishlist information
- Custom business dashboard
- Total and daily revenue statistics
- Recent-order monitoring
- Low-stock product monitoring

## Technologies

- Python 3.14
- Django 6.1
- SQLite
- HTML5
- CSS3
- Bootstrap 5
- JavaScript
- Pillow
- Git and GitHub

## Project Structure

```text
XCommerce/
├── accounts/
├── cart/
├── config/
├── core/
├── dashboard/
├── orders/
├── products/
├── wishlist/
├── static/
├── templates/
├── manage.py
├── requirements.txt
└── README.md
# XCommerce

XCommerce is a full-stack e-commerce web application built with Django.  
It provides product browsing, authentication, cart, wishlist, checkout,
Stripe test payments, order management, and an admin dashboard.

## Live Website

https://xcommerce.onrender.com

## Features

- User registration and email activation
- Login, logout, password reset, and profile management
- Product categories, search, filtering, and featured products
- Product details, stock management, discounts, and reviews
- Session-based shopping cart
- User wishlist
- Checkout and order history
- Cash on Delivery and Stripe test payments
- Payment status and order status management
- Django administration dashboard
- Persistent PostgreSQL database
- Cloudinary product and profile image storage
- Responsive Bootstrap interface
- Automated Django tests

## Technology Stack

### Backend

- Python
- Django 6.1
- PostgreSQL
- SQLite for local development

### Frontend

- HTML5
- CSS3
- Bootstrap 5
- JavaScript

### Services

- Stripe Checkout
- Cloudinary
- Render
- GitHub

## Local Installation

```bash
git clone https://github.com/fmuntasir751-prog/XCommerce.git
cd XCommerce

python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
http://127.0.0.1:8000/
DJANGO_SECRET_KEY
DJANGO_DEBUG
DJANGO_ALLOWED_HOSTS
DATABASE_URL

STRIPE_PUBLISHABLE_KEY
STRIPE_SECRET_KEY
STRIPE_WEBHOOK_SECRET

CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
python manage.py test
Card number: 4242 4242 4242 4242
Expiry: Any future date
CVC: Any three digits

তারপর:

```powershell
git add README.md
git commit -m "Add professional project README"
git push