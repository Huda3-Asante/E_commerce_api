cart_lists =[]
    get_product_id(cart.item.product_id)
    cart_lists.append(cart.model_dump())
    return{"message": "Product added successfully", "cart": cart}

    