# 🛒 Django E-Commerce Backend

A scalable and modular e-commerce backend built with Django and Django REST Framework. It supports user registration/login, product catalog, cart management, order placement, Razorpay integration for payments, and Celery for background email notifications.

---

## 🚀 Features

- JWT-based user authentication (Simple JWT)
- Product listing with search, filtering, and pagination
- Cart functionality: Add, update, remove items
- Order placement from cart
- Razorpay payment integration
- Celery + Redis for sending order confirmation emails
- Admin APIs to view and manage all orders

---

## 📦 Tech Stack

- Django & Django REST Framework
- PostgreSQL (or SQLite for development)
- Redis (for Celery broker)
- Celery (async background tasks)
- Razorpay (payment gateway)
- Docker (optional)
- AWS (EC2, RDS, S3 - for deployment)

---

## 🧱 Project Structure

```
ecommerce-backend/
├── core/                # Main Django app
│   ├── models.py        # User, Product, Cart, Order models
│   ├── views.py         # API views
│   ├── urls.py
│   ├── serializers.py
│   └── tasks.py         # Celery email task
├── ecommerce/           # Project settings
│   ├── settings.py
│   ├── urls.py
│   └── celery.py
├── manage.py
└── requirements.txt
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/aafankadri/ecommerce-backend.git
cd ecommerce-backend
```

### 2. Create Virtual Environment & Install Requirements

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure Environment Variables

In `ecommerce/settings.py`, set:

```python
RAZORPAY_KEY_ID = 'your_key_id'
RAZORPAY_KEY_SECRET = 'your_key_secret'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your_email'
EMAIL_HOST_PASSWORD = 'your_app_password'
```

---

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

---

### 6. Run Server

```bash
python manage.py runserver
```

---

## 🔋 Run Redis and Celery

### Start Redis (Linux/macOS)

```bash
sudo service redis-server start
```

### Start Celery Worker

```bash
celery -A ecommerce worker --loglevel=info
```

---

## 🔐 API Endpoints

### Authentication

| Endpoint              | Method | Description       |
|-----------------------|--------|-------------------|
| /api/register/        | POST   | Register user     |
| /api/token/           | POST   | Login (JWT)       |
| /api/token/refresh/   | POST   | Refresh token     |

### Products & Cart

| Endpoint              | Method | Description       |
|-----------------------|--------|-------------------|
| /api/products/        | GET    | List products     |
| /api/cart/            | GET    | View cart         |
| /api/cart/add/        | POST   | Add to cart       |
| /api/cart/update/<id> | PUT    | Update quantity   |
| /api/cart/remove/<id> | DELETE | Remove item       |

### Orders

| Endpoint                     | Method | Description             |
|------------------------------|--------|-------------------------|
| /api/orders/create/          | POST   | Place order (from cart) |
| /api/orders/                 | GET    | View user's orders      |
| /api/razorpay/create-order/  | POST   | Razorpay initiate       |
| /api/razorpay/verify-payment/| POST   | Confirm & place order   |

### Admin Only

| Endpoint                        | Method | Description              |
|---------------------------------|--------|--------------------------|
| /api/admin/orders/              | GET    | View all orders          |
| /api/admin/orders/<id>/update/  | PUT    | Update order status      |

---

## 📧 Email Notification (Celery)

- Order confirmation emails are sent in background after a successful order.


---

## 📝 License

MIT License

---

## 👨‍💻 Developed by

**Aafan Liyakat Ali Kadri**  
MSc in Computer Science (Scaler Neovarsity - Woolf)