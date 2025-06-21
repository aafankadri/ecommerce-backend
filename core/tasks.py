from celery import shared_task
from django.core.mail import send_mail
from .models import Order

@shared_task
def send_order_confirmation_email(order_id):
    try:
        order = Order.objects.get(id=order_id)
        subject = f"Order #{order.id} Confirmation"
        message = f"""
        Hi {order.user.full_name},

        Thank you for your order!

        Order ID: {order.id}
        Total: ₹{order.total_price}

        We'll notify you once it's shipped.
        """
        send_mail(
            subject,
            message,
            'aafan.kadri123@gmail.com',
            [order.user.email],
            fail_silently=False,
        )
        return "Email sent"
    except Order.DoesNotExist:
        return "Order not found"
