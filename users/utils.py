
from .models import Invoice, Order
from datetime import date
from datetime import datetime, timedelta


def add_date(date, days ):
    date = datetime.strptime(date, '%Y-%m-%d')

    # Add 5 days to the start_date
    modified_start_date = date + timedelta(days=days)
    return modified_start_date.strftime('%Y-%m-%d')


def ScheduledDelivery():
    orders = Order.objects.filter(next_date = date.today())
    for order in orders:
        invoice = Invoice(
            order = order,
            user= order.user,
            payment_type = 'scheduled'
        )
        invoice.save()
        order.status= "pending"
        match order.frequency:
            case "weekly":
                order.next_date= add_date(order.next_date, 7)

            case "fortnight":
                order.next_date= add_date(order.next_date, 15)

        order.save()
    print("scheduled delivery completed")