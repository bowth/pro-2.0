from django.shortcuts import render
from django.http import JsonResponse
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.views import generic
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy

def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	print(cartItems)
	order = data['order']
	items = data['items']
	if request.user.is_authenticated:
                auth = True
	else:
                auth = False
	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems, 'auth':auth}
	return render(request, 'store/store.html', context)


def sepet(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	if request.user.is_authenticated:
                auth = True
	else:
                auth = False
	context = {'items':items, 'order':order, 'cartItems':cartItems, 'auth':auth}
	return render(request, 'store/sepet.html', context)

def checkout(request):
	data = cartData(request)
	if request.user.is_authenticated:
		auth=True
	else:
		auth = False
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems, 'auth':auth}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	print(customer)
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()
	Order.objects.all().delete()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		mahalle=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)


class SignUpView(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'registration/signup.html'

def contacts(request):
	context = {}
	return render(request, 'store/contacts.html', context)

