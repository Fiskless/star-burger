from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http.response import Http404


from .models import Product
from .models import Order
from .models import OrderProduct


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    error = {}
    try:
        order_data = request.data
        if not isinstance(order_data['firstname'], str) \
            or not isinstance(order_data['lastname'], str) \
            or not isinstance(order_data['phonenumber'], str) \
            or not isinstance(order_data['address'], str):

            error = {"error": "the order key is not specified or not str"}

        if order_data['firstname'] == "" \
            or order_data['lastname'] == "" \
            or order_data['phonenumber'] == "" \
            or order_data['address'] == "":
            error = {"error": "order key is empty "}

        order = Order.objects.create(first_name=order_data['firstname'],
                                     last_name=order_data['lastname'],
                                     phone_number=order_data['phonenumber'],
                                     address=order_data['address'])

        if 'products' not in order_data \
            or not isinstance(order_data['products'], list) \
            or not order_data['products']:

            error = {"error": "products key not presented or not list"}

        else:
            for product in order_data['products']:
                try:
                    if not isinstance(product['product'], int):
                        error = {"error": "the product id is not specified or not str"}
                        break

                    product_name = Product.objects.get(id=product['product'])
                    product_quantity = product['quantity']
                    OrderProduct.objects.create(product=product_name,
                                                quantity=product_quantity,
                                                order=order)
                except Product.DoesNotExist:
                    error = {"error": "product id does not exist"}
    except KeyError:
        error = {"error": "order value not presented"}

    return Response(error)
