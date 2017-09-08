# -*- coding: utf-8 -*-
from trytond.model import fields, ModelSQL, ModelView
from trytond.pool import PoolMeta
from trytond.pyson import Eval, Bool

__all__ = ['Product', 'GiftCardPrice']
__metaclass__ = PoolMeta


class Product:
    "Product"
    __name__ = 'product.product'

    is_gift_card = fields.Boolean("Is Gift Card ?")

    gift_card_delivery_mode = fields.Selection([
        ('virtual', 'Virtual'),
        ('physical', 'Physical'),
        ('combined', 'Combined'),
    ], 'Gift Card Delivery Mode')

    allow_open_amount = fields.Boolean("Allow Open Amount ?")
    gc_min = fields.Numeric("Gift Card Minimum Amount")

    gc_max = fields.Numeric("Gift Card Maximum Amount")

    gift_card_prices = fields.One2Many(
        'product.product.gift_card.price', 'product', 'Gift Card Prices',
    )

    @classmethod
    def view_attributes(cls):
        return super(Product, cls).view_attributes() + [
            ('//page[@id="gift_card_details"]', 'states', {
                'invisible': ~Bool(Eval('is_gift_card'))
            })]

    @staticmethod
    def default_gift_card_delivery_mode():
        return 'physical'

    @staticmethod
    def default_is_gift_card():
        return False

    @staticmethod
    def default_allow_open_amount():
        return False

    @classmethod
    def __setup__(cls):
        super(Product, cls).__setup__()

        cls._error_messages.update({
            'inappropriate_product_type':
                'The product type of %s must be service for gift cards.',
            'invalid_amount':
                'Gift Card minimum amount must be smaller than gift card '
                'maximum amount',
            'negative_amount_not_allowed':
                'Gift card amounts can not be negative'
        })

    @classmethod
    def validate(cls, templates):
        """
        Validates each product template
        """
        super(Product, cls).validate(templates)

        for template in templates:
            template.check_product_type()
            template.check_gc_min_max()

    def check_gc_min_max(self):
        """
        Check minimum amount to be smaller than maximum amount
        """
        if not self.allow_open_amount:
            return

        if self.gc_min < 0 or self.gc_max < 0:
            self.raise_user_error("negative_amount_not_allowed")

        if self.gc_min > self.gc_max:
            self.raise_user_error("invalid_amount")

    def check_product_type(self):
        '''
        Product type of gift cards must be service.
        '''
        if not self.is_gift_card:
            return

        if self.type != 'service':
            self.raise_user_error(
                "inappropriate_product_type", (self.rec_name,)
                )


class GiftCardPrice(ModelSQL, ModelView):
    "Gift Card Price"
    __name__ = 'product.product.gift_card.price'
    _rec_name = 'price'

    product = fields.Many2One(
        "product.product", "Product", required=True, select=True
    )

    price = fields.Numeric("Price", required=True)

    @classmethod
    def __setup__(cls):
        super(GiftCardPrice, cls).__setup__()

        cls._error_messages.update({
            'negative_amount': 'Price can not be negative'
        })

    @classmethod
    def validate(cls, prices):
        """
        Validate product price for gift card
        """
        super(GiftCardPrice, cls).validate(prices)

        for price in prices:
            price.check_price()

    def check_price(self):
        """
        Price can not be negative
        """
        if self.price < 0:
            self.raise_user_error("negative_amount")
