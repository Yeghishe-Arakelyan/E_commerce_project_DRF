from shop_m.models import Product

class Cart:
    def __init__(self, request):
        self.request = request
        self.cart_data = self.get_cart_data()

    def add_to_cart(self, product_id, quantity):
        try:
            product = Product.objects.get(id=product_id)
            if str(product_id) not in self.cart_data:
                self.cart_data[str(product_id)] = {
                    'product_id': product_id,
                    'quantity': quantity,
                    'price': str(product.price),
                    'product_name': product.name,
                }
            else:
                self.cart_data[str(product_id)]['quantity'] += quantity
            self.save_cart_data()
            return True  
        except Product.DoesNotExist:
            return False  

    def remove_from_cart(self, product_id):
        if str(product_id) in self.cart_data:
            del self.cart_data[str(product_id)]
            self.save_cart_data()

    def get_cart_contents(self):
        cart_items = list(self.cart_data.values())
        return cart_items

    def calculate_total_price(self):
        total_price = sum(
            int(item['price']) * item['quantity'] for item in self.cart_data.values()
        )
        return total_price

    def clear_cart(self):
        self.cart_data = {}
        self.save_cart_data()

    def get_cart_data(self):
        return self.request.data.get('cart', {})

    def save_cart_data(self):
        self.request.data['cart'] = self.cart_data
