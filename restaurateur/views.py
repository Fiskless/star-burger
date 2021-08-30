from django import forms
from django.db.models import Q
from django.db.models.query import Prefetch
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.conf import settings

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views

from foodcartapp.models import Order, OrderProduct
from foodcartapp.models import RestaurantMenuItem
from foodcartapp.models import Product, Restaurant
from place.models import Place

import requests
from geopy import distance
from functools import reduce


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:

        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


def fetch_coordinates(apikey, place):

    base_url = "https://geocode-maps.yandex.ru/1.x"
    params = {"geocode":
                  place, "apikey": apikey, "format": "json"}
    response = requests.get(base_url, params=params)
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return Place.objects.create(address=place, lon=lon, lat=lat)


def get_place_coordinates(new_place, exists_places_data):
    if new_place not in exists_places_data:
        order_coordinates = fetch_coordinates(settings.GEO_APIKEY, new_place)
        return order_coordinates.lat, order_coordinates.lon
    order_coordinates_lat = exists_places_data[new_place].lat
    order_coordinates_lon = exists_places_data[new_place].lon
    return order_coordinates_lat, order_coordinates_lon


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):

    nonprocessed_orders = (
        Order.objects
            .filter(order_status='Необработанный')
            .prefetch_related('products')
            .order_price()
    )

    places = (
        Place.objects
            .filter(
                Q(address__in=nonprocessed_orders.values_list('address')) |
                Q(address__in=Restaurant.objects.values_list('address'))
            )
            .in_bulk(field_name='address')
    )
    # menu_items = (
    #     RestaurantMenuItem.objects
    #         .prefetch_related('restaurant', 'product')
    #         .available()
    #         .in_bulk()
    #         .values()
    # )
    #
    # # print(menu_items)
    products = Product.objects.all()
    restaurants = Restaurant.objects.all()
    products_with_restaurants = {
        product.id: restaurants.filter(menu_items__product__id=product.id) for
                                 product in products
    }
    # products_with_restaurants = { product
    #     for product in menu_items.products.all()
    # }
    # products_with_restaurants = {menu_item.product_id: menu_item.restaurant for
    #                              menu_item in menu_items}
    # print(products_with_restaurants)

    menu_items1 = (
        RestaurantMenuItem.objects
            .available()
    )
    # print(menu_items1)

    restaurants = (
        Restaurant.objects
            .prefetch_related(Prefetch('menu_items', menu_items1))
    )


    order_items = []
    for order in nonprocessed_orders:
        order_coordinates_lat, order_coordinates_lon = get_place_coordinates(order.address, places)

        order_products_ids = [order_product.product_id for order_product in order.products.all()]
        print(order_products_ids)
        restaurants = [products_with_restaurants[product_id] for product_id in order_products_ids]


        # print(order_products_ids)

        # restaurants_list1 = [
        #     restaurants.filter(Q(menu_items__product_id=order_product_id)) for
        #     order_product_id in order_products_ids
        # ]
        # print(restaurants_list1)
        # print(order_products)
        # restaurants_list =[
        #     restaurants.filter(menu_items__product_id=order_product_id) for order_product_id in order_products_ids
        # ]
        # print(restaurants_list)
        # menu_items5 = [rest.menu_items.all() for rest in restaurants]
        # print(menu_items5)

        # restaurant_list2 = [
        #     [menu_item.restaurant for menu_item in menu_items.filter(product_id=product_id)]
        #     for product_id in order_products_ids]
        # # print(restaurant_list2)

        # menu_items_ids = [menu_item.product_id for menu_item in menu_items]
        # print(menu_items_ids)
        # rest = menu_items[0].restaurant.all()
        # print(rest)

        # restaurants_list = [
        #     [menu_item.restaurant for menu_item in menu_items
        #      if menu_item.product_id == product_id] for product_id in
        #      order_products_ids]
        # # print(restaurants_list)
        #
        # restaurants_list1 = [
        #     menu_item.restaurant for menu_item in menu_items
        #      if menu_item.product_id in order_products_ids]
        # print(restaurants_list1)
        # print(restaurants_list1)


        # menu_items_with_restaurants = [
        #     order_product.product.menu_items.all() for order_product in order.products.all()
        # ]
        #
        # restaurants_list1 = [
        #     [menu_item.restaurant for menu_item in menu_items]
        #     for menu_items in menu_items_with_restaurants
        # ]

        #
        # print(restaurants_list1)
        # result_restaurant_list = restaurants_list[0]
        # for restaurant in restaurants_list:
        #     result_restaurant_list = (
        #             set(result_restaurant_list) & set(restaurant))
        # result_restaurant_list1 = restaurants_list1[0]
        # for restaurant in restaurants_list1:
        #     result_restaurant_list1 = (
        #         set(result_restaurant_list) & set(restaurant))

        result_restaurants = (reduce(lambda a, b: set(a) & set(b),
                                     restaurants))

        distance_to_restaurant = []

        for restaurant in result_restaurants:
            restaurant_coordinates_lat, restaurant_coordinates_lon = get_place_coordinates(
                restaurant.address, places)

            delivery_distance = distance.distance(
                (order_coordinates_lat, order_coordinates_lon),
                (restaurant_coordinates_lat, restaurant_coordinates_lon))

            distance_to_restaurant.append(round(delivery_distance.km, 3))

        restaurant_distance = dict(zip(result_restaurants,
                                            distance_to_restaurant))

        sorted_restaurant_distance_keys = sorted(restaurant_distance,
                                                      key=restaurant_distance.get)

        sorted_restaurant_distance = {
            key: restaurant_distance[key] for key in sorted_restaurant_distance_keys
        }

        order_items.append({
            'id': order.id,
            'order_status': order.order_status,
            'order_price': order.total_price,
            'client': f'{order.firstname} {order.lastname}',
            'phone': order.phonenumber,
            'address': order.address,
            'comment': order.comment,
            'payment_method': order.payment_method,
            'restaurant_distance': sorted_restaurant_distance
        })

    return render(request,
                  template_name='order_items.html',
                  context={'order_items': order_items})


