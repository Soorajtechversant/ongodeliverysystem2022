import os
import stripe
from django.shortcuts import  render
from django.views.generic import View
from django.views import View
from django.contrib import auth, messages
from django.shortcuts import redirect, render
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView  
from .forms import *
from .models import *
from .send_sms import sendsms






class HotelProducts(View):
    @method_decorator(login_required)
    def get(self, request, name):
        hotel = HotelName.objects.filter(hotelname=name)
        context = {
            'hotel': hotel
        }
        return render(request, 'hotelproducts.html', context)


# Customer Registration
class CustomerRegistration(View):
    def get(self, request):
        return render(request, 'products/registration/registration.html')

    def post(self, request):
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        address = request.POST['address']
        phn_number = request.POST['phn_number']
        user_type="customer"

        if password == password2:
            if UserLoginDetails.objects.filter(username=username).exists():
                messages.info(request, 'Username is already exist')
                return redirect('registration')
            else:
                login_cred = UserLoginDetails.objects.create(username=username,first_name=first_name, \
                    last_name=last_name,email=email,address=address, phn_number=phn_number,user_type=user_type)
                login_cred.set_password(password)
                login_cred.save()
                user = UserDetails.objects.create(
                    username=login_cred,first_name=first_name, last_name=last_name, email=email,address=address,phn_number=phn_number)
                user.save()
                # sendsms(phn_number)
                messages.info(request, 'customer registered')
                return redirect('auth/login')
        else:
            messages.info(request, 'password is not matching')
            return redirect('registration')

# MerchantRegistration


class MerchantRegistration(View):
    def get(self, request):
        return render(request, 'products/registration/merchantregistration.html')

    def post(self, request):
        global Registration
        global u1
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        hotelname = request.POST['hotelname']
        businesstype = request.POST['businesstype']
        username = request.POST['username']
        address = request.POST['address']
        u1 = username
        password = request.POST['password']
        password2 = request.POST['password2']
        user_type = "merchant"

        if password == password2:
            if UserLoginDetails.objects.filter(username=username).exists():
                messages.info(request, 'Username is already exist')
                return redirect('registration')
            else:
                login_cred = UserLoginDetails.objects.create(username=username,first_name=first_name, last_name=last_name, \
                                                email=email,address=address, phn_number=phone, user_type=user_type)
                login_cred.set_password(password)     
                login_cred.save() 
                print(login_cred)                          
                merchant = MerchantDetails.objects.create(username=login_cred,first_name=first_name, last_name=last_name, \
                                                email=email,address=address,phn_number=phone,hotel_name=hotelname, \
                                                    bussiness_type=businesstype)
                merchant.save()

                messages.info(request, 'Merchant registered')
                return redirect('owner_index')

        else:
            messages.info(request, 'password is not matching')
            return redirect('merchantregistration')


class Customer_index(View):
    def get(self, request):
        context = {
            'hotel': HotelName.objects.all()
        }
        print(HotelName.objects.all())
        
        return render(request, 'home.html', context)

# Common Login page


class Login(View):
    def get(self, request):
        return render(request, 'products/registration/login.html')

    def post(self, request):
        if request.method == 'POST':
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username, password=password)
            print(user)
            if user.user_type == "merchant":
                auth.login(request, user)
                return redirect('owner_index')
            elif user is not None:
                auth.login(request, user)
                return redirect("customer_index")
            else:
                messages.info(request, 'Invalid Credentials......')
                return redirect("login")

# The logout class


class Logout(View):
    def get(self, request):
        auth.logout(request)
        return redirect('/')


@login_required
def settings(request):
    membership = False
    cancel_at_period_end = False
    if request.method == 'POST':
        subscription = stripe.Subscription.retrieve(
            request.user.customer.stripe_subscription_id)
        subscription.cancel_at_period_end = True
        request.user.customer.cancel_at_period_end = True
        cancel_at_period_end = True
        subscription.save()
        request.user.customer.save()
    else:
        try:
            customer= Customer.objects.get(user__username=request.user.username)
            # customer = Customer.object.
            if customer.membership:
                membership = True
            if request.user.customer.cancel_at_period_end:
                cancel_at_period_end = True
        except Customer.DoesNotExist:
            membership = False
    return render(request, 'products/settings.html', {'membership': membership,
                                             'cancel_at_period_end': cancel_at_period_end})


class CustomerProfile(ListView):

    def post(self, request):
        data = UserLoginDetails.objects.get(username=request.user.username, )
        if len(request.FILES) != 0:
            if len(data.profile) > 0:
                os.remove(data.profile.path)
            data.profile = request.FILES['profile']

        data.username = request.POST.get('username')
        data.phone = request.POST.get('phone')
        data.email = request.POST.get('email')
        data.save()
        messages.success(request, " Updated Successfully")
        return redirect('profile')

    def get(self, request):
        data = UserLoginDetails.objects.get(username=request.user.username)
        context = {'data': data}
        return render(request, 'profile.html', context)


@method_decorator(login_required(login_url='/log/'), name='dispatch')
class EditProfile(View):
    def get(self, request, *args, **kwargs):
        data = User.objects.get(username=request.user)
        return render(request, "profile.html", {'obj': data})


class Owner_index(ListView):
    context_object_name = 'hotelname'
    queryset = HotelName.objects.all()
    template_name = "products/productshop_owner/owner_index.html"


# forloop

class Add_product(View):
    form_class = HotelForm

    def get(self, request):
        HotelForm = self.form_class()
        return render(request, "products/productshop_owner/add_product.html", {'form': HotelForm})

    def post(self, request):
        if request.method == 'POST':
            form = self.form_class(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                return redirect('owner_index')
            else:
                return redirect('add_product')


# This class will delete the product details
class Delete_product(View):
    def get(self, request, id):
        hotelname = HotelName.objects.get(id=id)
        hotelname.delete()
        return redirect("owner_index")


# This class will edit/update the product details
class Edit_product(View):
    def get(self, request, id):
        hotelname = HotelName.objects.get(id=id)
        form = HotelForm(instance=hotelname)
        return render(request, 'products/productshop_owner/edit_product.html', {'form': form})

    def post(self, request, id):
        if request.method == 'POST':
            hotelname = HotelName.objects.get(id=id)
            form = HotelForm(request.POST, request.FILES, instance=hotelname)
            print(form)
            if form.is_valid():
                form.save()
                return redirect("owner_index")


class ProductDetailView(View):
    @method_decorator(login_required)
    def get(self, request, id):

        product_details = HotelName.objects.filter(id=id)
        context = {
            'hotel': product_details
        }
        # context['stripe_publishable_key'] = STRIPE_PUBLISHABLE_KEY
        return render(request, 'hotelproducts.html', context)



