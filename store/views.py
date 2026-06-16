from django.shortcuts import render
from .models import Product, Order, OrderItem
from django.shortcuts import redirect
import razorpay
from django.conf import settings
from django.contrib.auth.decorators import login_required
from .models import Category
from django.contrib.auth import views as auth_views



def home(request):
    categories = Category.objects.all()
    return render(request, 'store/home.html', {'categories': categories})

def product_list(request):
    products = Product.objects.filter(available=True)
    return render(request, 'store/product_list.html', {'products': products})

def category_products(request, category_id):
    products = Product.objects.filter(category_id=category_id, available=True)
    return render(request, 'store/product_list.html', {'products': products})


from django.shortcuts import get_object_or_404

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    return render(request, 'store/product_detail.html', {'product': product})

from django.contrib import messages

@login_required
def add_to_cart(request, id):

    product = Product.objects.get(id=id)

    cart = request.session.get('cart', {})

    product_id = str(id)

    cart[product_id] = cart.get(product_id, 0) + 1

    request.session['cart'] = cart

    return redirect('cart_detail')

def cart_detail(request):
    cart = request.session.get('cart', {})
    products = []
    total = 0

    for product_id, quantity in cart.items():

        product = Product.objects.filter(id=product_id).first()

        if not product:
            continue

        product.quantity = quantity
        product.subtotal = product.price * quantity
        total += product.subtotal

        products.append(product)

    return render(request, 'store/cart.html', {
        'products': products,
        'total': total
    })

def remove_from_cart(request, id):
    cart = request.session.get('cart', {})

    if str(id) in cart:
        del cart[str(id)]

    request.session['cart'] = cart
    return redirect('cart_detail')
def increase_quantity(request, id):
    product = Product.objects.get(id=id)
    cart = request.session.get('cart', {})

    product_id = str(id)
    current_quantity = cart.get(product_id, 0)

    if current_quantity < product.stock:
        cart[product_id] = current_quantity + 1
        request.session['cart'] = cart
    else:
        messages.error(request, "Cannot add more. Stock limit reached!")

    return redirect('cart_detail')
def decrease_quantity(request, id):
    cart = request.session.get('cart', {})

    if str(id) in cart:
        cart[str(id)] -= 1

        if cart[str(id)] <= 0:
            del cart[str(id)]

    request.session['cart'] = cart
    return redirect('cart_detail')
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('product_list')

    total = 0
    order = Order.objects.create(total_amount=0)

    for product_id, quantity in cart.items():

        product = Product.objects.filter(id=product_id).first()

        if not product:
            continue

        subtotal = product.price * quantity
        total += subtotal

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

        product.stock -= quantity
        product.save()

    order.total_amount = total
    order.save()

    request.session['cart'] = {}

    return render(request, 'store/success.html', {'order': order})
def payment(request):

    cart = request.session.get('cart', {})
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        total += product.price * quantity

    amount = int(total * 100)

    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    payment = client.order.create({
        "amount": amount,
        "currency": "INR",
        "payment_capture": "1"
    })

    return render(request, "store/payment.html", {
        "payment": payment,
        "total": total,
        "razorpay_key": settings.RAZORPAY_KEY_ID
    })
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

def signup(request):

    if request.method == 'POST':
        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('login')

    else:
        form = UserCreationForm()

    return render(request, 'store/signup.html', {'form': form})

from .models import Address, Product
from django.contrib.auth.decorators import login_required

@login_required
def address(request):

    if request.method == "POST":

        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address_line = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')

        address = Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address_line=address_line,
            city=city,
            state=state,
            pincode=pincode
        )

        request.session['address_id'] = address.id

        return redirect('review_order')

    return render(request, 'store/address.html')
@login_required
def review_order(request):

    cart = request.session.get('cart', {})
    products = []
    total = 0

    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        product.quantity = quantity
        product.subtotal = product.price * quantity
        total += product.subtotal
        products.append(product)

    address_id = request.session.get('address_id')
    address = Address.objects.get(id=address_id)

    return render(request, 'store/review_order.html', {
        'products': products,
        'total': total,
        'address': address
    })
from django.contrib.auth.decorators import login_required
from .models import Order, OrderItem, Product

@login_required
def payment_success(request):

    cart = request.session.get('cart', {})

    if not cart:
        return redirect('home')

    total = 0

    order = Order.objects.create(
        user=request.user,
        total_amount=0
    )

    products = []

    for product_id, quantity in cart.items():

        product = Product.objects.get(id=product_id)

        subtotal = product.price * quantity
        total += subtotal

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price
        )

        product.stock -= quantity
        product.save()

        product.quantity = quantity
        product.subtotal = subtotal
        products.append(product)

    order.total_amount = total
    order.save()

    request.session['cart'] = {}

    return render(request, 'store/order_success.html', {
        'order': order,
        'products': products,
        'total': total
    })