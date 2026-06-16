def cart_context(request):
    """Make cart count and cart total available globally in all templates."""
    cart = request.session.get('cart', {})
    cart_count = sum(cart.values()) if cart else 0
    return {
        'cart_count': cart_count,
    }
