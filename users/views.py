
from django.contrib.auth import authenticate

from rest_framework.decorators import api_view,permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.paginator import Paginator

from .serializers import UserSerializer, LoginSerializer, UpdateUserSerializer,OrderSerializer, UrgentDeliverySerializer,InvoiceSerializer,MaintainenceSerializer, InvoiceInputSerializer,NotificationSerializer
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication

from .models import Customer,Invoice, Order, UrgentDelivery, Maintainence, Notification
from rest_framework.pagination import PageNumberPagination
from .utils import add_date

@api_view(["POST",])
def create(request):
    serializer = UserSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    serializer.perform_create(serializer)
    return Response(serializer.data)

@api_view(["POST",])
def login(request):
    
    serializer  = LoginSerializer(data =request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    email = serializer.data["email"]
    password = serializer.data["password"]
    
    user = authenticate(request=request,email=email, password=password)
    if user is None:
        return Response({
            "message": "enter valid email or password",
            }, status=status.HTTP_401_UNAUTHORIZED)
    refresh = RefreshToken.for_user(user)
    return Response({
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    })


@api_view(['PUT'])  # Example permission class
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def update_customer(request):
    try:
        customer = Customer.objects.get(pk=request.user.id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateUserSerializer(customer, data=request.data)

    if serializer.is_valid():

        serializer.update(customer, validated_data=request.data)
        return Response(serializer.data)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])  # Example permission class
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def user_details(request):
    
    try:
        customer = Customer.objects.get(pk=request.user.id)
    except Customer.DoesNotExist:
        return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = UpdateUserSerializer(customer)
    # if serializer.is_valid():
    return Response(serializer.data)
  


@api_view(["POST",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def create_order(request):
    user = request.user
    request.data["user"] = user.id
    start_date = request.data['start_date']
    frequency = request.data["frequency"]
    match frequency:
        case "weekly":
            request.data["next_date"] = add_date(start_date, 7)

        case "fortnight":
            request.data["next_date"] = add_date(start_date, 15)

    serializer  = OrderSerializer(data =request.data)    
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["POST",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def invoice(request):
    
    serializer  = InvoiceInputSerializer(data =request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    if serializer.data["type"] == "scheduled":
        order = Order.objects.get(pk = serializer.data["order_id"] )
        invoice = Invoice(
            order =order,
            user= request.user,
            payment_type = serializer.data["type"],
        )
        order.status = "pending"
        order.save()
        invoice.save()
    else:
        urgent_delivery = UrgentDelivery.objects.get(pk = serializer.data["order_id"] )
        invoice = Invoice(
            urgent_delivery = urgent_delivery,
            user_id = request.user.id,
            payment_type = serializer.data["type"],
        )
        urgent_delivery.status = "pending"
        urgent_delivery.save()
        invoice.save()
    
    return Response("your payment was successfull", status=status.HTTP_201_CREATED)


@api_view(["GET",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def all_invoices(request):
    
    user=request.user
    invoices = Invoice.objects.select_related('urgent_delivery').select_related('order').filter(user = user).order_by("-payment_date")
    paginator = Paginator(invoices, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    serializer = InvoiceSerializer(page_obj, many=True)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def invoice_details(request, pk):
    try:
        invoice = Invoice.objects.select_related('urgent_delivery').select_related('order').get(pk = pk)
    except Invoice.DoesNotExist:
        return Response({'error': 'invoice not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = InvoiceSerializer(invoice)
    
    return Response(serializer.data, status=status.HTTP_200_OK)



@api_view(["POST",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def urgent_delivery(request):
    user = request.user
    request.data["user"] = user.id
    
    serializer  = UrgentDeliverySerializer(data =request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)



@api_view(["POST",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def maintainence(request):
    
     
    user = request.user
    request.data["user"] = user.id
    serializer  = MaintainenceSerializer(data =request.data)

    
    if not serializer.is_valid():
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 1000


@api_view(["GET",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def history(request):
    
    user = request.user
    orders = Order.objects.filter(user=user)
    urgent_deliveries = UrgentDelivery.objects.filter(user=user)
    maintainences = Maintainence.objects.filter(user=user)
  # Serialize the objects
    orders_data = OrderSerializer(orders, many=True).data
    urgent_deliveries_data = UrgentDeliverySerializer(urgent_deliveries, many=True).data
    maintainences_data = MaintainenceSerializer(maintainences, many=True).data


    # Combine the serialized data
    combined_data = [
        {'type': 'order', 'data': order} for order in orders_data
    ] + [
        {'type': 'urgent_delivery', 'data': delivery} for delivery in urgent_deliveries_data
    ] + [
        {'type': 'maintainence', 'data': maintainence} for maintainence in maintainences_data
    ]


    return Response(combined_data, status=200)



@api_view(["GET",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def notification_details(request, pk):
    try:
        notification = Notification.objects.get(pk=pk)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = NotificationSerializer(notification)
    return Response(serializer.data, status=200)




@api_view(["GET",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def notifcation_latest(request):
    try:
        notification = Notification.objects.filter(user=request.user).order_by("-date").first()
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    serializer = NotificationSerializer(notification)
    return Response(serializer.data, status=200)




@api_view(["GET",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def notification_list(request):
    try:
        notifications = Notification.objects.filter(user=request.user).order_by("-date")
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    
    paginator = Paginator(notifications, 4)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    serializer = NotificationSerializer(page_obj, many=True)
    return Response(serializer.data, status=200)


@api_view(["PUT",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def notification_update(request, pk):
    
    try:
        notification = Notification.objects.get(pk=pk)
    except Notification.DoesNotExist:
        return Response({'error': 'Notification not found'}, status=status.HTTP_404_NOT_FOUND)
    notification.is_seen = not  notification.is_seen 
    notification.save()
    return Response('Status updated successfully', status = 200)


@api_view(["PUT",])
@permission_classes([IsAuthenticated])  # Ensure the user is authenticated
@authentication_classes([JWTAuthentication])
def update_order_status(request, pk):
    order_type = request.data["type"]
    match order_type:
        case "scheduled":
            try:
                order = Order.objects.get(pk=pk)
            except Notification.DoesNotExist:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        case "urgent":
            try:
                order = UrgentDelivery.objects.get(pk=pk)
            except Notification.DoesNotExist:
                return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
            
    order.status = "completed"
    order.save()
    return Response('Status updated successfully', status = 200)



