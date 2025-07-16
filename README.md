# Django E-commerce API

A robust, scalable RESTful API for e-commerce platforms built with Django and Django REST Framework. This project provides a comprehensive backend solution for modern e-commerce applications with features including user authentication, product catalog management, shopping cart functionality, order processing, and payment handling.

## 🚀 Features

- **User Management**: Custom user model with role-based access (Customer, Seller, Admin)
- **Authentication**: JWT-based authentication with token refresh
- **Product Catalog**: Complete product and category management with image support
- **Shopping Cart**: Full cart functionality for both authenticated and guest users with stock validation
- **Order Management**: End-to-end order lifecycle handling with order items
- **Payment Processing**: Flexible payment integration with transaction tracking
- **API Documentation**: Interactive API documentation with Swagger/ReDoc
- **Modular Architecture**: Organized into separate Django apps for maintainability and scalability
- **Permission System**: Granular permissions with read-only access for public endpoints

## 📋 Requirements

- Python 3.8+
- Django 5.2.4
- Django REST Framework 3.16.0
- djangorestframework-simplejwt 5.5.0
- drf-spectacular 0.28.0
- Other dependencies listed in requirements.txt

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
│   ├── carts/          # Shopping cart functionality
│   ├── orders/         # Order management
│   └── payments/       # Payment processing
├── ecommerce/          # Project configuration
├── manage.py
├── requirements.txt
└── README.md
```

## 🔗 API Endpoints

### Authentication
- `POST /api/accounts/register/` - User registration
- `POST /api/token/` - Obtain JWT token
- `POST /api/token/refresh/` - Refresh JWT token
- `GET /api/accounts/user/me/` - Get current user profile
- `POST /api/accounts/user/{id}/change_password/` - Change password

### Catalog
- `GET /api/catalog/products/` - List all products (public)
- `POST /api/catalog/products/` - Create a new product (admin only)
- `GET /api/catalog/products/{slug}/` - Get product details (public)
- `PUT /api/catalog/products/{slug}/` - Update product (admin only)
- `DELETE /api/catalog/products/{slug}/` - Delete product (admin only)
- `GET /api/catalog/categories/` - List all categories (public)
- `POST /api/catalog/categories/` - Create a new category (admin only)
- `GET /api/catalog/categories/{slug}/` - Get category details (public)

### Shopping Cart
- `GET /api/carts/carts/current/` - Get user's current cart
- `POST /api/carts/carts/add_item/` - Add item to cart
- `POST /api/carts/carts/remove_item/` - Remove item from cart
- `POST /api/carts/carts/update_item/` - Update cart item quantity
- `POST /api/carts/carts/clear/` - Clear cart
- `GET /api/carts/cart-items/` - List cart items

### Orders
- `GET /api/orders/orders/` - List user orders
- `POST /api/orders/orders/` - Create a new order
- `GET /api/orders/orders/{id}/` - Get order details
- `PUT /api/orders/orders/{id}/` - Update order status

### Payments
- `GET /api/payments/payments/` - List payments
- `POST /api/payments/payments/` - Create a new payment
- `GET /api/payments/payments/{id}/` - Get payment details
- `GET /api/payments/payment-transactions/` - List payment transactions

## 📊 Data Models

### User Model
- Extended Django's AbstractUser
- Added fields: email (unique), phone, role, address details
- Roles: Customer, Seller, Admin
- Built-in verification flags for email and phone

### Product & Category Models
- Products with SKU, name, slug, description, price, stock
- Categories with hierarchical structure (parent-child relationships)
- Support for multiple product images with ordering
- Automatic slug generation from names

### Cart & CartItem Models
- Support for both authenticated and guest users (session-based)
- Tracking of items, quantities, and prices
- Stock validation on cart operations
- Automatic price calculation and cart totals

### Order & OrderItem Models
- Order number, status tracking, total amount
- Linked to user and contains order items
- Status options: pending, processing, shipped, completed, cancelled
- Automatic total calculation from order items

### Payment Models
- Payment processing with transaction tracking
- Support for different payment statuses and currencies
- OneToOne relationship with orders
- Transaction history for audit trails

## 🔐 Authentication & Permissions

The API uses JWT (JSON Web Tokens) for authentication. Protected endpoints require the Authorization header with the format: `Bearer <token>`.

### Permission Levels:
- **Public**: Anyone can view products and categories
- **Authenticated**: Users can manage their own carts and orders
- **Admin**: Full CRUD access to products, categories, and all data

## 📚 API Documentation

Interactive API documentation is available at:
- Swagger UI: `/api/docs/swagger/`
- ReDoc: `/api/docs/redoc/`
- Schema: `/api/schema/`

## 🛒 Shopping Cart Features

- **Session-based carts** for guest users
- **User-based carts** for authenticated users
- **Stock validation** on add/update operations
- **Automatic price calculation** for cart items and totals
- **Cart item management** with quantity updates and removals
- **Cart persistence** across sessions

## 💳 Payment System

- **Multiple payment statuses**: pending, succeeded, failed, canceled
- **Transaction tracking** for audit and webhook handling
- **Payment-Order linking** with OneToOne relationship
- **Currency support** with ISO3 codes
- **Transaction history** with raw response storage

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 🚧 Development Status

This project is currently under active development. Recent improvements include:

### ✅ Completed Features:
- ✅ API documentation with Swagger/OpenAPI
- ✅ Enhanced cart functionality with stock validation
- ✅ Improved permission system with read-only public access
- ✅ Better cart management with session support
- ✅ Payment system with transaction tracking

### 🔄 In Progress:
- 🔄 Advanced payment gateway integrations
- 🔄 Enhanced error handling and validation
- 🔄 Comprehensive test coverage

### 📋 Planned Features:
- [ ] Product reviews and ratings
- [ ] Advanced search and filtering
- [ ] Email notifications
- [ ] Wishlist functionality
- [ ] Inventory tracking with low stock alerts
- [ ] Discount and coupon system
- [ ] User address book
- [ ] Order history and reordering
- [ ] Multi-vendor marketplace support
- [ ] Advanced analytics and reporting

## ⚠️ Important Notes

- This project uses SQLite for development. For production, configure a production database (PostgreSQL recommended)
- Secret keys and sensitive settings should be moved to environment variables for production
- CORS headers are configured for development; adjust for production domains
- The current payment system is a foundation - integrate with actual payment gateways for production use

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