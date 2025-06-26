from django.shortcuts import get_object_or_404, redirect
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from decimal import Decimal
import stripe
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from store.models import Category, Product, Cart, CartOrder, CartOrderItem
from account.models import User
from store.serializer import CategorySerializer, ProductSerializer, CartSerializer, CartOrderSerializer

stripe.api_key = settings.STRIPE_SECRET_KEY

class CategoryListAPIView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (AllowAny,)

class ProductListAPIView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

class ProductDetailsAPIView(generics.RetrieveAPIView):
    serializer_class = ProductSerializer
    permission_classes = (AllowAny,)

    def get_object(self):
        slug = self.kwargs['slug']
        return get_object_or_404(Product, slug=slug)

class CartAPIView(generics.ListCreateAPIView):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        payload = request.data

        product_id = payload.get('product_id')
        user_id = payload.get('user_id')
        qty = payload.get('qty')
        price = payload.get('price')
        shipping_amount = payload.get('shipping_amount')
        country = payload.get('country')
        size = payload.get('size')
        color = payload.get('color')
        cart_id = payload.get('cart_id')

        product = get_object_or_404(Product, id=product_id)
        user = get_object_or_404(User, id=user_id)

        try:
            qty = Decimal(qty)
            price = Decimal(price)
            shipping_amount = Decimal(shipping_amount)
        except:
            return Response({"detail": "Invalid numeric values."}, status=status.HTTP_400_BAD_REQUEST)

        if qty <= 0:
            return Response({"detail": "Quantity must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        if price <= 0:
            return Response({"detail": "Price must be greater than 0."}, status=status.HTTP_400_BAD_REQUEST)
        if shipping_amount < 0:
            return Response({"detail": "Shipping amount cannot be negative."}, status=status.HTTP_400_BAD_REQUEST)
        if not size or not color:
            return Response({"detail": "Size and color must be selected."}, status=status.HTTP_400_BAD_REQUEST)

        cart = Cart.objects.filter(cart_id=cart_id, product=product, user=user).first()

        if cart:
            cart.qty = qty
            cart.price = price
            cart.shipping_amount = shipping_amount * qty
            cart.sub_total = price * qty
            cart.country = country
            cart.size = size
            cart.color = color
            cart.service_fee = Decimal('0.00')
            cart.text_fee = Decimal('0.00')
            cart.total = cart.sub_total + cart.shipping_amount
            cart.save()

            return Response({
                'message': 'Cart updated successfully.',
                'data': self.get_serializer(cart).data
            }, status=status.HTTP_200_OK)
        else:
            sub_total = price * qty
            shipping_total = shipping_amount * qty
            service_fee = Decimal('0.00')
            text_fee = Decimal('0.00')
            total = sub_total + shipping_total + service_fee + text_fee

            cart = Cart.objects.create(
                product=product,
                user=user,
                qty=qty,
                price=price,
                shipping_amount=shipping_total,
                text_fee=text_fee,
                sub_total=sub_total,
                country=country,
                size=size,
                color=color,
                cart_id=cart_id,
                service_fee=service_fee,
                total=total
            )

            return Response({
                'message': 'Product added to cart successfully.',
                'data': self.get_serializer(cart).data
            }, status=status.HTTP_201_CREATED)

class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        user_id = self.kwargs.get('user_id')

        if user_id:
            user = get_object_or_404(User, id=user_id)
            return Cart.objects.filter(cart_id=cart_id, user=user)
        return Cart.objects.filter(cart_id=cart_id)

class CartDetailsView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = (AllowAny,)
    lookup_field = 'cart_id'

    def get_queryset(self):
        cart_id = self.kwargs['cart_id']
        user_id = self.kwargs.get('user_id')

        if user_id:
            user = get_object_or_404(User, id=user_id)
            return Cart.objects.filter(cart_id=cart_id, user=user)
        return Cart.objects.filter(cart_id=cart_id)

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        total_shipping = sum([item.shipping_amount for item in queryset])
        total_tax = sum([item.text_fee for item in queryset])
        total_service_fee = sum([item.service_fee for item in queryset])
        total_sub_total = sum([item.sub_total for item in queryset])
        total_total = sum([item.total for item in queryset])

        data = {
            "shipping": total_shipping,
            "tax": total_tax,
            "service_fee": total_service_fee,
            "sub_total": total_sub_total,
            "total": total_total,
        }
        return Response(data, status=status.HTTP_200_OK)

class CartItemDeleteAPIView(generics.DestroyAPIView):
    serializer_class = CartSerializer
    lookup_field = 'cart_id'

    def get_object(self):
        cart_id = self.kwargs['cart_id']
        item_id = self.kwargs['item_id']
        user_id = self.kwargs.get('user_id')

        if user_id:
            user = get_object_or_404(User, id=user_id)
            return get_object_or_404(Cart, id=item_id, cart_id=cart_id, user=user)
        return get_object_or_404(Cart, id=item_id, cart_id=cart_id)

class CartOrderAPIView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    queryset = CartOrder.objects.all()
    permission_classes = (AllowAny,)

    def create(self, request):
        payload = request.data
        cart_id = payload.get('cart_id')
        user_id = payload.get('user_id')
        address = payload.get('address')
        full_name = payload.get('fullName')
        phone = payload.get('phone')
        email = payload.get('email')
        country = payload.get('country')
        state = payload.get('state')
        city = payload.get('city')
        pincode = payload.get('pincode')

        user = get_object_or_404(User, id=user_id) if user_id != 0 else None

        cart_items = Cart.objects.filter(cart_id=cart_id)
        total_shipping = Decimal('0.00')
        total_tax = Decimal('0.00')
        total_service_fee = Decimal('0.00')
        total_sub_total = Decimal('0.00')
        total_initial_total = Decimal('0.00')
        total_total = Decimal('0.00')

        order = CartOrder.objects.create(
            buyer=user,
            address=address,
            full_name=full_name,
            phone=phone,
            email=email,
            country=country,
            state=state,
            city=city,
            zipcode=pincode,
        )

        for c in cart_items:
            CartOrderItem.objects.create(
                order=order,
                product=c.product,
                qty=c.qty,
                color=c.color,
                size=c.size,
                price=c.price,
                shipping_amount=c.shipping_amount,
                text_fee=c.text_fee,
                service_fee=c.service_fee,
                sub_total=c.sub_total,
                total=c.total,
                initial_total=c.total,
            )

            total_shipping += c.shipping_amount
            total_tax += c.text_fee
            total_service_fee += c.service_fee
            total_sub_total += c.sub_total
            total_initial_total += c.total
            total_total += c.total

        order.shipping_amount = total_shipping
        order.text_fee = total_tax
        order.service_fee = total_service_fee
        order.sub_total = total_sub_total
        order.initial_total = total_initial_total
        order.total = total_total
        order.save()

        Cart.objects.filter(cart_id=cart_id).delete()

        if user_id != 0:
            return Response({"message": "Order Placed Successfully.", "order_oid": order.oid}, status=status.HTTP_201_CREATED)
        return Response({"message": "Order Placed Successfully."}, status=status.HTTP_200_OK)

class StripeCheckoutView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = (AllowAny,)
    queryset = CartOrder.objects.all()

    def create(self, request, *args, **kwargs):
        order_oid = self.kwargs.get('order_oid')
        order = get_object_or_404(CartOrder, oid=order_oid)

        try:
            checkout_session = stripe.checkout.Session.create(
                customer_email=order.email,
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': order.full_name},
                        'unit_amount': int(order.total * 100),
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'http://localhost:5173/payment-success/{order.oid}?session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url='http://localhost:5173/payment-failed/',
            )
            order.stripe_session_id = checkout_session.id
            order.save()
            return redirect(checkout_session.url)
        except stripe.error.StripeError as e:
            return Response({"message": f"Error creating checkout session: {str(e)}."}, status=status.HTTP_400_BAD_REQUEST)

class PaymentSuccessView(generics.CreateAPIView):
    serializer_class = CartOrderSerializer
    permission_classes = (AllowAny,)
    queryset = CartOrder.objects.all()

    def create(self, request, *args, **kwargs):
        payload = request.data
        order_oid = payload.get('order_oid')
        session_id = payload.get('session_id')
        order = get_object_or_404(CartOrder, oid=order_oid)
        order_items = CartOrderItem.objects.filter(order=order)

        if session_id != 'null':
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                if order.payment_Status != 'paid':
                    order.payment_Status = 'paid'
                    order.save()

                    # product quantity update
                    for item in order_items:
                        product = item.product
                        if product.stock_qty >= item.qty:
                            product.stock_qty -= item.qty
                            product.save()

                    # send emails
                    context = {'order': order, 'order_item': order_items}
                    subject = "Order Placed successfully"
                    text_body = render_to_string('emails/customer_order_placed.txt', context)
                    html_body = render_to_string('emails/customer_order_placed.html', context)
                    msg = EmailMultiAlternatives(subject, text_body, settings.EMAIL_HOST_USER, [order.email])
                    msg.attach_alternative(html_body, 'text/html')
                    msg.send()

                    for item in order_items:
                        context = {'order': order, 'order_item': order_items, 'vendor': item.vendor}
                        subject = "Order Placed successfully"
                        text_body = render_to_string('emails/vendor_order_placed.txt', context)
                        html_body = render_to_string('emails/vendor_order_placed.html', context)
                        msg = EmailMultiAlternatives(subject, text_body, settings.EMAIL_HOST_USER, [item.vendor.email])
                        msg.attach_alternative(html_body, 'text/html')
                        msg.send()

                    return Response({"message": "payment Successful"}, status=status.HTTP_200_OK)
                else:
                    return Response({"message": "Already paid"}, status=status.HTTP_200_OK)
            elif session.payment_status == 'pending':
                return Response({"message": "Order Payment Pending."}, status=status.HTTP_200_OK)
            elif session.payment_status == 'canceled':
                return Response({"message": "Order Payment Cancelled."}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Order Payment Failed. Try again"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Invalid session id."}, status=status.HTTP_400_BAD_REQUEST)
