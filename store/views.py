from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import views as auth_views
from django.contrib import messages
from django.conf import settings
from django.db.models import Q
from .models import Product, Order, OrderItem, Category, Address
import razorpay


def home(request):
    categories = Category.objects.all()
    featured_products = Product.objects.filter(available=True).order_by('-created_at')[:8]
    return render(request, 'store/home.html', {
        'categories': categories,
        'featured_products': featured_products,
    })


def product_list(request):
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()

    # Search functionality
    query = request.GET.get('q', '')
    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )

    # Category filter
    category_id = request.GET.get('category', '')
    selected_category = None
    if category_id:
        try:
            selected_category = Category.objects.get(id=category_id)
            products = products.filter(category=selected_category)
        except Category.DoesNotExist:
            pass

    # Sort
    sort = request.GET.get('sort', '')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'name':
        products = products.order_by('name')

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': selected_category,
        'current_sort': sort,
    })


def category_products(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    products = Product.objects.filter(category=category, available=True)
    categories = Category.objects.all()

    sort = request.GET.get('sort', '')
    if sort == 'price_low':
        products = products.order_by('price')
    elif sort == 'price_high':
        products = products.order_by('-price')
    elif sort == 'newest':
        products = products.order_by('-created_at')
    elif sort == 'name':
        products = products.order_by('name')

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'selected_category': category,
        'current_sort': sort,
    })


def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    # Related products from same category
    related_products = Product.objects.filter(
        category=product.category, available=True
    ).exclude(id=product.id)[:4] if product.category else Product.objects.filter(
        available=True
    ).exclude(id=product.id)[:4]

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
    })


@login_required
def add_to_cart(request, id):
    product = Product.objects.get(id=id)
    cart = request.session.get('cart', {})
    product_id = str(id)
    cart[product_id] = cart.get(product_id, 0) + 1
    request.session['cart'] = cart
    messages.success(request, f'"{product.name}" added to cart!')
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
        'total': total,
    })


def remove_from_cart(request, id):
    cart = request.session.get('cart', {})
    if str(id) in cart:
        del cart[str(id)]
    request.session['cart'] = cart
    messages.success(request, 'Item removed from cart.')
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

    if not cart:
        messages.error(request, "Your cart is empty. Please add items to proceed.")
        return redirect('cart_detail')

    total = 0
    for product_id, quantity in cart.items():
        product = Product.objects.filter(id=product_id).first()
        if product:
            total += product.price * quantity

    if total == 0:
        messages.error(request, "Invalid order amount.")
        return redirect('cart_detail')

    amount = int(total * 100)

    try:
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
    except Exception as e:
        messages.error(request, f"Error initializing payment gateway: {str(e)}")
        return redirect('cart_detail')


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created successfully! Please log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'store/signup.html', {'form': form})


@login_required
def address(request):
    if request.method == "POST":
        full_name = request.POST.get('full_name')
        phone = request.POST.get('phone')
        address_line = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        pincode = request.POST.get('pincode')

        addr = Address.objects.create(
            user=request.user,
            full_name=full_name,
            phone=phone,
            address_line=address_line,
            city=city,
            state=state,
            pincode=pincode
        )
        request.session['address_id'] = addr.id
        return redirect('review_order')

    # Load saved addresses for the user
    saved_addresses = Address.objects.filter(user=request.user).order_by('-created_at')[:1]
    return render(request, 'store/address.html', {
        'saved_addresses': saved_addresses,
    })


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
    addr = Address.objects.get(id=address_id)

    return render(request, 'store/review_order.html', {
        'products': products,
        'total': total,
        'address': addr,
    })


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
        'total': total,
    })


@login_required
def track_order(request):
    order_id = request.GET.get('order_id')
    order = None
    error = None

    if order_id:
        try:
            clean_id = ''.join(filter(str.isdigit, order_id))
            if not clean_id:
                raise ValueError("Invalid ID format")
            order = Order.objects.get(id=clean_id, user=request.user)
        except (Order.DoesNotExist, ValueError):
            error = "Order not found. Please check your Order ID."

    return render(request, 'store/track_order.html', {
        'order': order,
        'error': error,
        'searched': bool(order_id),
    })


@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        orders = orders.filter(status=status_filter)

    return render(request, 'store/my_orders.html', {
        'orders': orders,
        'current_status': status_filter,
    })