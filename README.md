# Store_X E-Commerce Website

A full-stack E-Commerce web application built using Django that allows users to browse products, manage their cart, place orders, and make payments through Razorpay.

## Live Demo

https://store-x-ecom.onrender.com/

---

## Features

* User Registration & Login
* Product Listing & Details
* Category-wise Product Browsing
* Shopping Cart
* Address Management
* Order Placement
* Razorpay Payment Integration
* Order Tracking
* Responsive User Interface
* Admin Panel for Product Management

---

## Tech Stack

### Backend

* Python
* Django

### Frontend

* HTML
* CSS
* JavaScript

### Database

* SQLite

### Deployment

* Render

### Payment Gateway

* Razorpay

### Version Control

* Git & GitHub

---

## Project Structure

```text
Store_X/
│
├── ecommerce/
├── store/
├── templates/
├── media/
├── manage.py
├── requirements.txt
├── render.yaml
└── build.sh
```

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/prashantyadavv/Store_X-Ecom.git
cd Store_X-Ecom
```

### Create Virtual Environment

```bash
python -m venv env
```

### Activate Environment

Windows:

```bash
env\Scripts\activate
```

Mac/Linux:

```bash
source env/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Migrations

```bash
python manage.py migrate
```

### Start Development Server

```bash
python manage.py runserver
```

Visit:

```text
http://127.0.0.1:8000/
```

---

## Environment Variables

Create a `.env` file and add:

```env
SECRET_KEY=your_secret_key

RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret

DEBUG=True
```

---

## Learning Outcomes

Through this project I gained practical experience in:

* Django Development
* Authentication & Authorization
* Payment Gateway Integration
* Database Management
* Git & GitHub Workflow
* Cloud Deployment with Render
* Debugging Production Issues
* Full-Stack Web Development

---

## Future Improvements

* PostgreSQL Integration
* Product Search & Filters
* Wishlist Functionality
* Email Notifications
* Inventory Management
* Admin Analytics Dashboard

---

## Author

Prashant Yadav

GitHub: https://github.com/prashantyadavv

---

## License

This project is built for educational and portfolio purposes.
