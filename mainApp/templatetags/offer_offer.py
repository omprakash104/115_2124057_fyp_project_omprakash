from django import template

register = template.Library()

import math
@register.simple_tag
def call_sellprice(marked_price,selling_price):
    if selling_price == None or selling_price == 0:
        return marked_price
    sellprice = marked_price
    # sellprice = marked_price - (marked_price * discount/100)
    sellprices = (marked_price - selling_price)
    sellprice =  (sellprices/marked_price)*100
    return math.floor(sellprice)