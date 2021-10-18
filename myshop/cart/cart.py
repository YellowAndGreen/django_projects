from decimal import Decimal
from django.conf import settings
from django.forms import model_to_dict

from shop.models import Product


class Cart(object):

    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            # save an empty cart in the session
            # 本质是键值对
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def __iter__(self):
        """
        Iterate over the items in the cart and get the products
        from the database.
        """
        # 会话的键列表
        product_ids = self.cart.keys()
        # in关键字：以一个列表查找，对里面每个元素查找的结果放在一起
        products = Product.objects.filter(id__in=product_ids)

        cart = self.cart.copy()
        for product in products:
            # 加入product实例
            cart[str(product.id)]['product'] = product
            # cart[str(product.id)]['product'] = {'url': product.get_absolute_url(), 'image': product.image,
            #                                     'image_url': product.image.url, 'name': product.name}
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        # 转为str是因为json键只能是string
        product_id = str(product.id)
        if product_id not in self.cart:
            self.cart[product_id] = {'quantity': 0,
                                     'price': product.price}
            # print(list(self.cart))
        if override_quantity:
            self.cart[product_id]['quantity'] = quantity
        else:
            self.cart[product_id]['quantity'] += quantity
        # print(product_id)
        self.save()

    def save(self):
        # mark the session as "modified" to make sure it gets saved
        self.session.modified = True

    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.save()

    def clear(self):
        # remove cart from session
        del self.session[settings.CART_SESSION_ID]
        self.save()

    def get_total_price(self):

        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())