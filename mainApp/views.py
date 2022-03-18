from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView, CreateView
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy

from .models import *

# Create your views here.
class BaseView(View):
	views = {}

class HomeView(TemplateView,BaseView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        self.views['sliders'] = Slider.objects.all()
        context['product_list'] = Product.objects.all().order_by("-id")[:8]
        return context
    
    


class ContactView(TemplateView):
    template_name = "contact-us.html"
    

class AboutView(TemplateView):
    template_name = "about-us.html"


class ShopView(TemplateView):
    template_name = "shop.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['allcategories'] = Product.objects.all()
        return context

    # def get(self, request):
    #     self.views['allcategories'] = Product.objects.all()
    #     paginator = Paginator(self.views['allcategories'], 1) # Show 25 contacts per page.
    #     page_number = request.Get.get('page')
        
    #     self.views['page_obj'] = paginator.get_page(page_number)

class ProductDetailView(TemplateView):
    template_name = "product-details.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Product.objects.get(slug=url_slug)
        product.view_count += 1
        product.save()
        context['product'] = product
        return context

class AddToCartView(TemplateView):
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

class EmptyCartView(View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("mainApp:mycart")

class ManageCartView(View):
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



class MyCartView(TemplateView):
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

class CheckoutView(TemplateView):
    template_name = "checkout.html"
    # from_class = CheckoutForm
    sucess_url = reverse_lazy("mainApp:home")
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
        else:
            cart_obj = None
        context['cart'] = cart_obj
        return context



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

def signup(request):
	if request.method == 'POST':
		username = request.POST['username']
		email = request.POST['email']
		password = request.POST['password']
		cpassword = request.POST['cpassword']

		if password == cpassword:
			if User.objects.filter(username = username).exists():
				messages.error(request,'The username is already taken')
				return redirect('/signup')
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
				messages.success(request,'You are registered!')
				return redirect('/signup')

	return render(request,'signup.html')
				    
class Search(BaseView):
	def get(self,request):
		query = request.GET.get('query',None)
		if not query:
			return redirect('/')
		self.views['search_query'] = Product.objects.filter(title__icontains = query)
		return render(request,'search.html',self.views)