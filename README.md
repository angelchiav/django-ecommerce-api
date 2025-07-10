# Django E-commerce API

A modular and scalable RESTful API for an e-commerce platform built with Django and Django REST Framework. This project provides a robust backend solution for modern e-commerce applications with features including user authentication, product catalog management, and order processing.

## 🚀 Features

- **User Management**: Custom user model with role-based access (Customer, Seller, Admin)
- **Authentication**: Secure user registration and authentication system
- **Product Catalog**: Complete product and category management
- **Order Management**: Full order lifecycle handling with order items
- **RESTful API**: Clean and intuitive API endpoints following REST principles
- **Modular Architecture**: Organized into separate Django apps for maintainability

## 📋 Requirements

- Python 3.8+
- Django 5.2.4
- Django REST Framework 3.16.0
- SQLite (default) or PostgreSQL/MySQL for production

## 🛠️ Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/django-ecommerce-api.git
cd django-ecommerce-api
```

2. **Create a virtual environment**
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Run migrations**
```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Create a superuser**
```bash
python manage.py createsuperuser
```

6. **Run the development server**
```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/`

## 📁 Project Structure

```
django-ecommerce-api/
├── apps/
│   ├── accounts/       # User authentication and profiles
│   ├── catalog/        # Products and categories
│   └── orders/         # Order management
├── ecommerce/          # Project configuration
├── manage.py
├── requirements.txt
└── README.md
```

## 🔗 API Endpoints

### Authentication
- `POST /api/accounts/register/` - User registration
- `GET /api/accounts/user/me/` - Get current user profile
- `POST /api/accounts/user/{id}/change_password/` - Change password

### Catalog
- `GET /api/catalog/products/` - List all products
- `POST /api/catalog/products/` - Create a new product
- `GET /api/catalog/products/{slug}/` - Get product details
- `PUT /api/catalog/products/{slug}/` - Update product
- `DELETE /api/catalog/products/{slug}/` - Delete product

- `GET /api/catalog/categories/` - List all categories
- `POST /api/catalog/categories/` - Create a new category
- `GET /api/catalog/categories/{slug}/` - Get category details

### Orders
- `GET /api/orders/orders/` - List user orders
- `POST /api/orders/orders/` - Create a new order
- `GET /api/orders/orders/{id}/` - Get order details
- `PUT /api/orders/orders/{id}/` - Update order status

## 📊 Data Models

### User Model
- Extended Django's AbstractUser
- Added fields: email (unique), phone, role, address details
- Roles: Customer, Seller, Admin

### Product Model
- SKU, name, slug, description, price, stock
- Many-to-many relationship with categories
- Support for multiple product images

### Order Model
- Order number, status tracking, total amount
- Linked to user and contains order items
- Status options: pending, processing, shipped, completed, cancelled

## 🔐 Authentication

The API uses Django's built-in authentication system with token-based authentication for API access. Protected endpoints require authentication headers.

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 🚧 Development Status

This project is currently under active development. The following features are planned:

- [ ] Payment integration
- [ ] Shopping cart functionality
- [ ] Product reviews and ratings
- [ ] Advanced search and filtering
- [ ] Email notifications
- [ ] API documentation with Swagger/OpenAPI
- [ ] Wishlist functionality
- [ ] Inventory tracking
- [ ] Discount and coupon system

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under a custom license. See the [LICENSE](LICENSE) file for details.

**Note**: Commercial use requires explicit permission from the author.

## 👤 Author

**Angel Chia Vicuña**
- Email: achiavicuna@gmail.com

## 🙏 Acknowledgments

- Django Software Foundation for the amazing framework
- Django REST Framework team for the powerful API toolkit
- All contributors who help improve this project

---
