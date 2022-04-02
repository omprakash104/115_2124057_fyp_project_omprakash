from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, DetailView, FormView, ListView
from django.contrib import messages
from django.contrib.auth.models import User
from .models import User
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import *

from .models import *

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

class HomeView(Ecomrequired,TemplateView,BaseView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.views['sliders'] = Slider.objects.all()
        context['product_list'] = Product.objects.all().order_by("-id")[:8]
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

    # def get(self, request):
    #     self.views['allcategories'] = Product.objects.all()
    #     paginator = Paginator(self.views['allcategories'], 1) # Show 25 contacts per page.
    #     page_number = request.Get.get('page')
        
    #     self.views['page_obj'] = paginator.get_page(page_number)

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
    template_name = "cart.html"

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
                cartproduct.subtotal += product_obj.selling_prince
                cartproduct.save()
                cart_obj.total += product_obj.selling_prince
                cart_obj.save()
                # messages.success(request,'product is already exists!')
            #for new item id added in cart
            else:
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.selling_prince, quantity=1, subtotal=product_obj.selling_prince
                )
                cart_obj.total += product_obj.selling_prince
                cart_obj.save()
                # messages.success(request,'New product are added!')


        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                    cart=cart_obj, product=product_obj, rate=product_obj.selling_prince, quantity=1, subtotal=product_obj.selling_prince
                )
            cart_obj.total += product_obj.selling_prince
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

class CheckoutView(Ecomrequired, TemplateView):
    template_name = "checkout.html"
    # from_class = CheckoutForm
    sucess_url = reverse_lazy("mainApp:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.customer:
            pass
        else:
            return redirect("/signup/")
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

    def get_context(request):
        if request.method == 'POST':
            order = Order()
            full_name = request.POST['fname']
            address = request.POST['address']
            phone = request.POST['pnumber']
            memail = request.POST['femail']

            order.ordered_by = full_name
            order.email = memail
            order.shipping_address = address
            order.mobile = phone
            cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            order.cart = cart_obj
            order.subtotal = cart_obj.total
            order.discount = 0
            order.total = cart_obj.total
            order.order_status = "Order Received"
            del request.session['cart_id']  
            order.save()
        return render(request, 'checkout.html')



class BlogView(TemplateView):
    template_name = "blog.html"

@login_required
def review(request):	
	username = request.user.username
	email = request.user.email
	slug = request.POST.get('slug')
	comment = request.POST.get('comment')
	data = Review.objects.create(
		username = username,
		email = email,
		slug = slug,
		comment = comment
		)
	data.save()
	return render(request,'/home')
	# return redirect(f"/product/{slug}")

# def signup(request):
# 	if request.method == 'POST':
# 		username = request.POST['username']
# 		email = request.POST['email']
# 		password = request.POST['password']
# 		cpassword = request.POST['cpassword']

# 		if password == cpassword:
# 			if User.objects.filter(username = username).exists():
# 				messages.error(request,'The username is already taken')
# 				return redirect('/signup')
# 			elif User.objects.filter(email = email).exists():
# 				messages.error(request,'The email is already taken')
# 				return redirect('/signup')
# 			else:
# 				user = User.objects.create_user(
# 					username = username,
# 					email = email,
# 					password = password
# 					)
# 				user.save()
#                 customer = Customer()



# 				messages.success(request,'You are registered!')
# 				return redirect('/signup')

# 	return render(request,'signup.html')
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
                    return redirect("/signup")
                elif User.objects.filter(email = email).exists():
                    messages.error(request,'The email is already taken')
                    return redirect('/signup')
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
                    return redirect("/signup")
        return render(request,"signup.html")

				    
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
