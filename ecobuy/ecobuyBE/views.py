from django.http import HttpResponse
from json import JSONDecodeError, loads
from ecobuyBE.models import EcoUser, Product
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
import ast

def index(request):
    users = EcoUser.objects.all()
    products = Product.objects.all()
    context = {"users": users, "products": products}
    template = "index.html"
    return render(request, template, context)

def handle_post(request):
    if request.method == "POST":
        if request.body:
            try:
                return loads(request.body)
            except JSONDecodeError as e:
                raise e
            except TypeError as e:
                raise Exception(e)
        else:
            raise Exception("Post request has not body")
    else:
        raise Exception("Post request expected")

def set_user_rate(user_email, new_product_rate, user_country):
    print("test")
    if EcoUser.objects.filter(email=user_email).exists():
        print("exists")
        #compute new rate
        user = EcoUser.objects.get(email=user_email)
        user.ecobuy_rate = (user.ecobuy_rate * user.number_of_products + new_product_rate)/ (user.number_of_products +1)
        user.number_of_products += 1
       
    else:
        #create user
        user = EcoUser(email=user_email, country=user_country, ecobuy_rate=new_product_rate, number_of_products=1)
    
    user.save()
    return user

def save_new_product(user, name, rate, price, country, dimensions, weight, material):
    product = Product(user=user, name=name, ecobuy_rate=rate, price=price, country=country, dimensions=dimensions, weight=weight, material=material)
    product.save()
    return product
    
@csrf_exempt
def user_buy_product(request):
    # http POST http://127.0.0.1:8000/user_buy/ user_email="david" user_country="USA" product_name="product" product_rate=70 product_price="10" product_country="USA" product_dimensions="3x3x3" product_weight="48lbs" product_material="aluminium"
    # http GET http://127.0.0.1:8000/ecobuy
    # http POST http://10.219.128.29:8000/user_buy/ user_email="david" user_country="USA" product_name="product" product_rate=0.5 product_price="10" product_country="USA" product_dimensions="3x3x3" product_weight="48lbs" product_material="aluminium"
    # python manage.py runserver 172.20.10.10:8000
    try:
        received_json_data = ast.literal_eval(request.body.decode('utf8').replace("'", '"'))
        print("la")
        user_email = received_json_data["user_email"]
        print(user_email)
        user_country = received_json_data["user_country"]
        product_name = received_json_data["product_name"]
        product_rate = float(received_json_data["product_rate"])
        product_price = received_json_data["product_price"]
        product_country = received_json_data["product_country"]
        product_dimensions = received_json_data["product_dimensions"]
        product_weight = received_json_data["product_weight"]
        product_material = received_json_data["product_material"]
        user = set_user_rate(user_email, product_rate, user_country)
        save_new_product(user, product_name, product_rate, product_price, product_country, product_dimensions, product_weight, product_material)
        return HttpResponse(user)
        
    except Exception as e:
        return HttpResponse(e)
        
    
@csrf_exempt
def get_user_data(request):
    received_json_data = ast.literal_eval(request.body.decode('utf8').replace("'", '"'))
    user_email = received_json_data["user_email"]
    rate = 0
    products25 = 0
    products50= 0
    products75 = 0
    products100 = 0
    if EcoUser.objects.filter(email=user_email).exists():
        #compute new rate
        user = EcoUser.objects.get(email=user_email)
        rate = user.ecobuy_rate
        products25 = Product.objects.filter(user=user).filter(ecobuy_rate__gte=0).filter(ecobuy_rate__lte=25).count()
        products50 = Product.objects.filter(user=user).filter(ecobuy_rate__gte=25).filter(ecobuy_rate__lte=50).count()
        products75 = Product.objects.filter(user=user).filter(ecobuy_rate__gte=50).filter(ecobuy_rate__lte=75).count()
        products100 = Product.objects.filter(user=user).filter(ecobuy_rate__gte=75).filter(ecobuy_rate__lte=100).count()

    data = {"user": user_email,"user_rate": str(rate),"products25": str(products25),"products50": str(products50),"products75": str(products75),"products100": str(products100)}
    
    return HttpResponse(json.dumps(data))
        
       

 
    
    
    