from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from products import products

# Creates a FastAPI Server
app = FastAPI()

class User(BaseModel):
    id: int
    username: str
    email: str
    password: str

class Item(BaseModel):
    product_id: int
    quantity: int

class Cart(BaseModel):
    user_id: int
    item: Item

# creates a list to store registered users
users = []

carts = {}


@app.get("/")
def get_home():
    return {"message": "Welcome to our E-commerce Website"}

# get all products
@app.get("/products")
def get_products():
    return {"products": products}

# gets one product by id
@app.get("/products/{product_id}")
def get_product_id(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")

# registers a new user
@app.post("/register")
def register_user(user: User):
    users.append(user.model_dump())
    return {"message": "You're successfully registered!", "user": user}

# logs users in
@app.post("/login")
def login_user(login_data: User):
    for user in users:
        if user["username"] == login_data.username and user["password"] == login_data.password:
            return {"message": "Login Successful!"}
    return {"error": "Invalid username or password!!!"}


# adds an item to cart
@app.post("/cart")
def add_to_cart(cart: Cart):
    # check if product exists
    product = next((p for p in products if p["id"] == cart.item.product_id), None)
    if not product:
        return {"error": "Invalid product ID. Product not found!"}

    # create cart for user if not exists
    if cart.user_id not in carts:
        carts[cart.user_id] = []

    # check if product already in cart, update quantity
    for item in carts[cart.user_id]:
        if item["product_id"] == cart.item.product_id:
            item["quantity"] += cart.item.quantity
            return {"message": "Product quantity updated", "cart": carts[cart.user_id]}

    # otherwise add new item
    carts[cart.user_id].append({
        "product_id": cart.item.product_id,
        "quantity": cart.item.quantity
    })

    return {"message": "Product added successfully", "cart": carts[cart.user_id]}

# get a user's cart
@app.get("/cart/{user_id}")
def get_cart(user_id: int):
    if user_id not in carts or not carts[user_id]:
        return {"message": "Cart is empty", "cart": []}
    return {"user_id": user_id, "cart": carts[user_id]}

# checkout
@app.post("/checkout/{user_id}")
def checkout(user_id: int):
    if user_id not in carts or not carts[user_id]:
        return {"message": "Cart is empty", "order_summary": []}

    cart_items = []
    total = 0

    for item in carts[user_id]:
        product = next((p for p in products if p["id"] == item["product_id"]), None)
        if not product:
            continue  

        subtotal = product["price"] * item["quantity"]
        total += subtotal

        cart_items.append({
            "product_id": item["product_id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": item["quantity"],
            "subtotal": subtotal
        })

    return {
        "user_id": user_id,
        "items": cart_items,
        "total": total
    }