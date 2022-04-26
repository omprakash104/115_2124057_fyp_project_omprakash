from msilib.schema import ListView
from multiprocessing import context
from sre_constants import SUCCESS
from urllib import request
from wsgiref.util import request_uri
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, FormView, DetailView, ListView, CreateView
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import CheckoutForm
from .models import *
from .forms import *
import requests
from .models import User
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.db.models import Q
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.files.storage import FileSystemStorage
from .templatetags.predict import predict_one_image, process_image
# Create your views here.
class BaseView(View):

	views = {}

class Ecomrequired(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.customer:
                cart_obj.customer = request.user.customer
                cart_obj.save()

        return super().dispatch(request, *args, **kwargs)

class HomeView(Ecomrequired,TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['slider'] = HomeSlider.objects.all()[:3]
        # context['banner'] = HomeBanner.objects.all()[:3]
        context['featured_product'] = Product.objects.all().order_by("id")[:6]
        context['product_list'] = Product.objects.all()[:8]
        return context
    

class ContactView(Ecomrequired,TemplateView):
    template_name = "contact-us.html"
    

class AboutView(Ecomrequired,TemplateView):
    template_name = "about-us.html"


class ShopView(Ecomrequired,TemplateView):
    template_name = "shop.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_products = Product.objects.all()
        paginator = Paginator(all_products, 4)
        page_number = self.request.GET.get('page')
        product_list = paginator.get_page(page_number)
        context['allcategories'] = product_list
        return context


class ProductDetailView(Ecomrequired,TemplateView):
    template_name = "product-details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Product.objects.get(slug=url_slug)
        product.view_count += 1
        product.save()
        context['product'] = product
        return context

class AddToCartView(Ecomrequired,TemplateView):
    template_name = "addtocart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #for get product id from requested url
        product_id = self.kwargs['pro_id']
        #for get product
        product_obj = Product.objects.get(id=product_id)
        #for cart ma aagadi xavane check garne
        cart_id = self.request.session.get("cart_id",None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(
                product=product_obj)
            #for items already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.selling_price
                cartproduct.save()
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
                # messages.success(request,'product is already exists!')
            #for new item id added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price
                )
                cart_obj.total += product_obj.selling_price
                cart_obj.save()
                # messages.success(request,'New product are added!')


        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price
                )
            cart_obj.total += product_obj.selling_price
            cart_obj.save()

        return context

class EmptyCartView(Ecomrequired,View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("mainApp:mycart")

class ManageCartView(Ecomrequired, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart
        
        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()

        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
            
        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass

        return redirect("mainApp:mycart")

class MyCartView(Ecomrequired, TemplateView):
    template_name = "cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        else:
            cart = None
        context['cart'] = cart
        return context


class AddToWishlistView(Ecomrequired, TemplateView):
    template_name = "addtowishlist.html"
    

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #for get product id from requested url
        product_id = self.kwargs['pro_id']
        #for get product
        product_obj = Product.objects.get(id=product_id)
        #for cart ma aagadi xavane check garne
        wishlist_id = self.request.session.get("wishlist_id",None)
        if wishlist_id:
            wishlist_obj = Wishlist.objects.get(id=wishlist_id)
            this_product_in_wishlist = wishlist_obj.wishlistproduct_set.filter(
                product=product_obj)
            
            #for items already exists in cart
            #for items already exists in cart
            if this_product_in_wishlist.exists():
                wishlistproduct = this_product_in_wishlist.last()
                wishlistproduct.quantity += 1
                wishlistproduct.subtotal += product_obj.selling_price
                wishlistproduct.save()
                wishlist_obj.total += product_obj.selling_price
                wishlist_obj.save()
                
            #for new item id added in cart
            else:
                wishlistproduct = WishlistProduct.objects.create(
                    wishlist=wishlist_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price
                )
                wishlist_obj.total += product_obj.selling_price
                wishlist_obj.save()

        else:
            wishlist_obj = Wishlist.objects.create(total=0)
            self.request.session['wishlist_id'] = wishlist_obj.id
            wishlistproduct = WishlistProduct.objects.create(
                    wishlist=wishlist_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price
                )
            wishlist_obj.total += product_obj.selling_price
            wishlist_obj.save()

        return context

class ManageWishlistView(Ecomrequired, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = WishlistProduct.objects.get(id=cp_id)
        wishlist_obj = cp_obj.wishlist
        
        if action == "rmv":
            wishlist_obj.total -= cp_obj.subtotal
            wishlist_obj.save()
            cp_obj.delete()
            
        else:
            pass

        return redirect("mainApp:mywishlist")

class MyWishListView(TemplateView):
    template_name = "wishlist.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        wishlist_id = self.request.session.get("wishlist_id", None)
        if wishlist_id:
            wishlist = Wishlist.objects.get(id=wishlist_id)
        else:
            wishlist = None
        context['wishlist'] = wishlist
        return context

class AddToCompareView(Ecomrequired, TemplateView):
    template_name = "addtocompare.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #for get product id from requested url
        product_id = self.kwargs['pro_id']
        #for get product
        product_obj = Product.objects.get(id=product_id)
        #for cart ma aagadi xavane check garne
        compare_id = self.request.session.get("compare_id",None)
        if compare_id:
            compare_obj = Compare.objects.get(id=compare_id)
            this_product_in_compare = compare_obj.compareproduct_set.filter(
                product=product_obj)
            
            #for items already exists in cart
            if this_product_in_compare.exists():
                compareproduct = this_product_in_compare.last()
                compareproduct.save()
                
            #for new item id added in cart
            else:
                compareproduct = CompareProduct.objects.create(
                    compare=compare_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price
                )
                compare_obj.total += product_obj.selling_price
                compare_obj.save()


        else:
            compare_obj = Compare.objects.create(total=0)
            self.request.session['compare_id'] = compare_obj.id
            compareproduct = CompareProduct.objects.create(
                    compare=compare_obj, product=product_obj, rate=product_obj.selling_price, quantity=1, subtotal=product_obj.selling_price
                )
            compare_obj.total += product_obj.selling_price
            compare_obj.save()

        return context
class ManageCompareView(Ecomrequired, View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CompareProduct.objects.get(id=cp_id)
        compare_obj = cp_obj.compare
        
        if action == "rmv":
            compare_obj.total -= cp_obj.subtotal
            compare_obj.save()
            cp_obj.delete()
            
        else:
            pass

        return redirect("mainApp:mycompare")
class MyCompareView(Ecomrequired, TemplateView):
    template_name = "compare.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        compare_id = self.request.session.get("compare_id", None)
        if compare_id:
            compare = Compare.objects.get(id=compare_id)
        else:
            compare = None
        context['compare'] = compare
        return context

class CheckoutView(Ecomrequired, CreateView):
    template_name = "checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("mainApp:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context

    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            form.instance.cart = cart_obj
            form.instance.subtotal = cart_obj.total
            form.instance.discount = 0
            form.instance.total = cart_obj.total
            form.instance.order_status = "Order Received"
            del self.request.session['cart_id']
            pm = form.cleaned_data.get("payment_method")
            order = form.save()
            if pm == "Khalti":
                return redirect(reverse("mainApp:khaltirequest") + "?o_id=" + str(order.id))
        else:
            return redirect("mainApp:home")
        return super().form_valid(form)


class KhaltiRequestView(View):
    def get(self, request, *args, **kwargs):
        o_id = request.GET.get("o_id")
        order = Order.objects.get(id=o_id)
        context = {
            "order": order
        }
        return render(request, "khaltirequest.html", context)

class KhaltiVerifyView(View):
    def get(self, request, *args, **kwargs):
        token = request.GET.get("token")
        amount = request.GET.get("amount")
        o_id = request.GET.get("order_id")
        url = "https://khalti.com/api/v2/payment/verify/"
        payload = {
            "token": token,
            "amount": amount
        }
        headers = {
            "Authorization": "test_secret_key_379b4dba87c4444bb22413f299a1878a"
        }
        order_obj = Order.objects.get(id=o_id)
        response = requests.post(url, payload, headers=headers)
        resp_dict = response.json()
        if resp_dict.get("idx"):
            success = True
            order_obj.patment_completed = True
            order_obj.save()
        else:
            success = False
        data = {
            "success": success
        }
        return JsonResponse(data)

class BlogView(TemplateView):
    template_name = "blog.html"

# @login_required
# def review(request):	
# 	username = request.user.username
# 	email = request.user.email
# 	slug = request.POST.get('slug')
# 	comment = request.POST.get('comment')
# 	data = Review.objects.create(
# 		username = username,
# 		email = email,
# 		slug = slug,
# 		comment = comment
# 		)
# 	data.save()
# 	return render(request,'/home')
# 	# return redirect(f"/product/{slug}")

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        full_name = request.POST['fullname']
        address = request.POST['address']
        email = request.POST['email']
        password = request.POST['password']
        cpassword = request.POST['cpassword']
            
        if password == cpassword:
            if User.objects.filter(username = username).exists():
                messages.error(request,'The username is already taken')
                return redirect("mainApp:customerregistration")
            elif User.objects.filter(email = email).exists():
                messages.error(request,'The email is already taken')
                return redirect("mainApp:customerregistration")
            else:
                user = User.objects.create_user(
				username = username,
				email = email,
				password = password
				)
                user.save()
                
                customer = Customer()
                customer.user = User.objects.get(username=user)
                customer.full_name = full_name
                customer.address = address
                customer.save()
                messages.success(request,'You are registered!')
                return redirect("mainApp:customerlogin")
    return render(request,"signup.html")

def view_authenticate_user(request):
    if request.method == "GET": 
        return render(request, 'login.html') 
    else:
        print(request.POST)
        user = authenticate(username=request.POST['username'], password=request.POST['password']) 
        print(user)
        if user is not None and Customer.objects.filter(user=user).exists():  
            login(request, user)
            messages.warning(request,'Login sucessfully')
            # if "next" in request.GET:
            #     next_url = request.GET.get("next")
            #     return next_url
            # else:
            #     return redirect("mainApp:customerlogin")

            return redirect("mainApp:home")   
            
        else: 
            messages.warning(request,'Please chek your username and password!!')
            return redirect("mainApp:customerlogin") 

class Search(BaseView):
	def get(self,request):
		query = request.GET.get('query',None)
		if not query:
			return redirect('/')
		self.views['search_query'] = Product.objects.filter(title__icontains = query)
		return render(request,'search.html',self.views)

class CustomerProfileView(TemplateView):
    template_name = "my-account.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/signup")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer = self.request.user.customer
        context["customer"] = customer
        orders = Order.objects.filter(cart__customer=customer).order_by("-id")
        context["orders"] = orders
        return context

class CustomerOrderDetailView(DetailView):
    template_name = "customerorderdetails.html"
    model = Order
    context_object_name = "ord_obj"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Customer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.customer != order.cart.customer: #authenticated for other customer ordered details
                return redirect("mainApp:customerprofile")
        else:
            return redirect("/signup")
        return super().dispatch(request, *args, **kwargs)

class AdminLoginView(FormView):
    template_name = "adminpages/adminlogin.html"
    form_class = LoginView
    success_url = reverse_lazy("mainApp:adminhome")

    def form_valid(self, form):
        uname = form.cleaned_data.get("username")
        pword = form.cleaned_data["password"]
        usr = authenticate(username=uname, password=pword)
        if usr is not None and Admin.objects.filter(user=usr).exists():
            login(self.request, usr)
        else:
            return render(self.request, self.template_name, {"form": self.form_class, "error": "Incorrect username and password"})


        return super().form_valid(form)

class AdminRequiredMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Admin.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/admin-login/")
        return super().dispatch(request, *args, **kwargs)

class AdminLogoutView(View):
    def get(self,request):
        logout(request)
        return redirect("mainApp:adminhome")


class AdminHomeView(AdminRequiredMixin, TemplateView):
    template_name = "adminpages/adminhome.html"


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pendingorders"] = Order.objects.filter(order_status="Order Received")

        return context

class AdminOrderDetailView(AdminRequiredMixin, DetailView):
    template_name = "adminpages/adminorderdetail.html"
    model = Order
    context_object_name = "order_obj"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context

class AdminOrderListView(AdminRequiredMixin, ListView):
    template_name = "adminpages/adminorderlist.html"
    queryset = Order.objects.all().order_by("-id")
    context_object_name = "allorders"

class AdminOrderStatusChangeView(AdminRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy("mainApp:adminorderdetail", kwargs={"pk": self.kwargs["pk"]}))


# for detection app views
def upload(request):
    context = {}
    if request.method == 'POST':
        uploaded_file = request.FILES['document']
        fs = FileSystemStorage()
        name = fs.save(uploaded_file.name, uploaded_file)
        context['url'] = fs.url(name)
        context['filename'] = name
        pred, probability, text = process_image(name)
 
        context['probability'] = probability
        context['text'] = text

    return render(request, 'upload.html', context)

