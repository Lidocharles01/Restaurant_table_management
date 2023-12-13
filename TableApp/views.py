from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Category, Item, Register_table, Booking,HomeDelivery
from django.db.models import F, Sum
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import re

def home(request):
    return render(request, 'index.html')


def shop_home(request):
    return render(request, 'Shop_home.html')

def table(request):
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]  # Replace this with your actual list of items
    return render(request, 'pick_table.html', {'items': items})

def take(request):
    items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]  # Replace this with your actual list of items
    return render(request, 'take_away.html', {'items': items})

def signin(request):
    if request.method == 'POST':
        un = request.POST['username']
        pwd = request.POST['password']

        user = authenticate(username=un, password=pwd)

        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful')
            return redirect('TableApp:shop_home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'signin.html')

def signout(request):
    logout(request)
    return redirect('/')

def signup(request):
    if request.method == 'POST':
        un = request.POST['username']
        pass1 = request.POST['password1']
        pass2 = request.POST['password2']

        if len(pass1) < 8 or not re.search("[!@#$%^&*()_+-=]", pass1):
            messages.error(request, 'Password must be at least 8 characters and contain at least one special character')
            return redirect('TableApp:signup')

        if pass1 != pass2:
            messages.error(request, 'Passwords do not match')
            return redirect('TableApp:signup')
        elif User.objects.filter(username=un).exists():
            messages.error(request, 'Username already exists')
            return redirect('TableApp:signup')
        else:
            usr = User.objects.create_user(un, '', pass1)
            usr.save()

            reg = Register_table(user=usr, loginid=un)
            reg.save()

            messages.success(request, 'Account created successfully')
            return render(request, 'signin.html', {"status": "Dear {} your account created successfully".format(un)})

    return render(request, 'signup.html')

def category_list(request):
    shop = request.user.register_table
    categories = Category.objects.filter(shop=shop)
    return render(request, 'category_list.html', {'categories': categories})

def add_category(request):
    if request.method == 'POST':
        shop = request.user.register_table
        name = request.POST['name']
        image = request.FILES.get('image')

        Category.objects.create(shop=shop, name=name, image=image)
        return redirect('TableApp:category_list')

    return render(request, 'add_category.html')

def edit_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    if request.method == 'POST':
        category.name = request.POST['name']
        category.image = request.FILES.get('image')
        category.save()
        return redirect('TableApp:category_list')
    return render(request, 'edit_category.html', {'category': category})

def delete_category(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    category.delete()
    return redirect('TableApp:category_list')

def add_item(request):
    if request.method == 'POST':
        shop = request.user.register_table
        category_id = request.POST['category']
        category = get_object_or_404(Category, pk=category_id, shop=shop)
        barcode = request.POST['barcode']
        tax = request.POST['tax']
        name = request.POST['name']
        price = request.POST['price']

        Item.objects.create(category=category, barcode=barcode, tax=tax, name=name, price=price)
        messages.success(request, 'Item added successfully')
        return redirect('TableApp:all_items')
    else:
        shop = request.user.register_table
        categories = Category.objects.filter(shop=shop)
        return render(request, 'add_item.html', {'categories': categories})

def edit_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'POST':
        item.name = request.POST['name']
        item.price = request.POST['price']
        item.barcode = request.POST['barcode']
        item.tax = request.POST['tax']
        item.save()
        return redirect('TableApp:all_items')

    return render(request, 'edit_item.html', {'item': item})

def delete_item(request, item_id):
    item = get_object_or_404(Item, pk=item_id)

    if request.method == 'POST':
        item.delete()
        return redirect('TableApp:all_items')

    return render(request, 'delete_item.html', {'item': item})

def item_details(request, item_id):
    item = get_object_or_404(Item, pk=item_id)
    return render(request, 'item_details.html', {'item': item})

def add_to_booking(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(Item, pk=item_id)
        user = request.user
        quantity_change = int(request.POST.get('quantity_change', 0))

        # Delete existing booking (if any)
        Booking.objects.filter(user=user, item=item, payment_received=False).delete()

        # Create a new booking
        booking = Booking.objects.create(
            user=user,
            item=item,
            quantity=quantity_change,
            total_amount=quantity_change * item.price,
            is_completed=True  # Mark the booking as completed
        )

        # Mark the corresponding item as booked
        item.is_booked = True
        item.save()

    return redirect('TableApp:booking', item_id=item_id)

def generate_booking_pdf(response, item, aggregated_booking):
    response['Content-Type'] = 'application/pdf'
    response['Content-Disposition'] = f'attachment; filename="booking_details_{item.name}.pdf"'

    p = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    center_style = ParagraphStyle('CenteredText', parent=styles['BodyText'], alignment=1)
    story = []

    title = f'Booking Details for {item.name}'
    story.append(Paragraph(title, styles['Title']))

    item_details = [
        f'Item: {item.name}',
        f'Quantity: {aggregated_booking["total_quantity"]}',
        f'Total Amount: {aggregated_booking["total_amount"]}',
    ]

    story.extend([Paragraph(detail, center_style) for detail in item_details])
    p.build(story)

def booking(request, item_id):
    user = request.user
    item = get_object_or_404(Item, pk=item_id)

    aggregated_booking = Booking.objects.filter(user=user, item=item, payment_received=False).values('item').annotate(
        total_quantity=Sum('quantity'),
        total_amount=Sum('total_amount')
    ).first()

    if not aggregated_booking:
        return render(request, 'booking.html', {'aggregated_booking': None, 'item': item})

    if request.GET.get('format') == 'pdf':
        response = HttpResponse(content_type='application/pdf')
        generate_booking_pdf(response, item, aggregated_booking)
        return response
    else:
        return render(request, 'booking.html', {'aggregated_booking': aggregated_booking, 'item': item})

def all_items(request):
    shop = request.user.register_table
    items = Item.objects.filter(category__shop=shop).select_related('category').all()
    return render(request, 'all_items.html', {'items': items})

def home_delivery(request):
    if request.method == 'POST':
        # Assuming you have a form on the frontend to collect delivery details
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        # Create a HomeDelivery instance without checking for an active booking
        delivery = HomeDelivery.objects.create(name=name, phone=phone, address=address)

        print("Form submitted successfully!")

        return redirect('TableApp:all_items')

    return render(request, 'home_delivery.html')