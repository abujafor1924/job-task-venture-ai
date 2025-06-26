# job-task-venture-ai

﻿# 🛒 Django Job Task – Ecommerce  API

A minimal **Ecommerce API** built using **Django** and **Django REST Framework**. This app allows authenticated users to manage cart items — adding, updating, removing, clearing, and calculating the total price.

---

## 📌 Task Summary

> ✅ Completed as per the job task requirements with the following features:

## Features

### User Authentication & Management
- User Registration with email verification  
- User Login with JWT token authentication  
- Password Reset via email verification  
- Password Change for authenticated users  

### Cart Management
- Add item to cart  
- Remove item from cart  
- Update quantity of cart items  
- View all cart items for a user  


### Order & Payment
- Create order from cart items  
- Stripe payment integration for checkout  
- Payment success confirmation  

### Product & Category Management
- List all product categories  
- View product list  
- View product details by slug  

### API Documentation
- Swagger UI documentation for easy API exploration and testing  

### Additional Features
- JWT Token refresh support  
- User profile view and update  
- Jaszzmin Dashbord Use
- Swagger UI Use
---

## 🧱 Project Structure


---

## 🚀 Setup Instructions

### 🔧 1. Clone the repository
```bash
gh repo clone abujafor1924/job-task-venture-ai
cd job-task

python -m venv env
Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate

python manage.py createsuperuser

python manage.py runserver

---
## Api Instraction
### API Documentation
- Swagger UI documentation for easy API exploration and testing  
## API Endpoints

### User Authentication & Profile
| Method | URL                          | Description                            |
|--------|------------------------------|--------------------------------------|
| POST   | `/user/token/`                | Obtain JWT token                      |
| POST   | `/user/token/refresh/`        | Refresh JWT token                    |
| POST   | `/user/register/`             | Register new user                    |
| POST   | `/user/password-reset/<email>/` | Request password reset via email  |
| POST   | `/user/password-change/`      | Change password (authenticated)     |
| GET    | `/user/profile/<user_id>/`    | Get user profile                     |

### Store - Categories & Products
| Method | URL                          | Description                         |
|--------|------------------------------|-----------------------------------|
| GET    | `/categories/`                | List all categories                |
| GET    | `/products/`                 | List all products                  |
| GET    | `/products/<slug>/`          | Product details by slug            |

### Cart Management
| Method | URL                                 | Description                        |
|--------|-------------------------------------|----------------------------------|
| GET    | `/cart/`                            | Create new cart or list carts     |
| GET    | `/cart/<cart_id>/`                  | List cart items by cart ID        |
| GET    | `/cart/details/<cart_id>/`          | Get detailed cart info            |
| DELETE | `/cart/<cart_id>/item/<item_id>/delete/` | Delete a specific cart item      |

### Orders & Payments
| Method | URL                                | Description                      |
|--------|------------------------------------|--------------------------------|
| POST   | `/order/`                         | Create order from cart          |
| GET    | `/checkout/<order_oid>/`          | Stripe checkout session         |
| GET    | `/payment-success/`               | Payment success confirmation    |

---

# You can showing all api 
main_url= http://127.0.0.1:8000/
api_test_url= http://127.0.0.1:8000/api/v1/
like: http://127.0.0.1:8000/api/v1/cart/

