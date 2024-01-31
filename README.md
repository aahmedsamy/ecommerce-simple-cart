[# Simple Ecommerce Cart

## Author
Ahmed Samy

## Getting Started

### Prerequisites
- Docker
- Docker Compose

### Running the Project
1. Clone the repository:
   ```bash
   git clone https://github.com/aahmedsamy/ecommerce-simple-cart.git
   cd ecommerce-simple-cart
   mv .env.example .env
2. Build and run the Docker containers:
   ```bash
   docker-compose -f docker-compose.dev.yml up --build -d
   
3. Navigate into the Docker container:
   ```bash
   docker exec -it ecommerce_cart-backend-container /bin/sh
4. Run Django migrations:
   ```bash
   python manage.py migrate
5. Load initial data into the database (example: loading products from ../db_dummy_data/products.json):
   ```bash
   python manage.py loaddata ../db_dummy_data/products.json
6. To run tests.
   ```bash
   pytest
----
Open your browser and go to http://localhost:8000 to start testing the app.

### Testing the App
- Visit http://localhost:8000/api/schema/swagger-ui/#/ in your browser. 
- Use the Swagger UI interface to explore and test the available API endpoints. 
- Navigate to http://localhost:8000/api/schema/swagger-ui/#/customers/customers_create and create a Customer user. Use its ID in all other requests.
### Notes
Ensure that Docker and Docker Compose are installed on your machine before running the project.
If you encounter any issues, refer to the project's documentation or contact the author.  