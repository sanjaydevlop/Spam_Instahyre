# splitwise/apis.py
from rest_framework.decorators import api_view
from django.contrib.auth.hashers import make_password,check_password
from rest_framework.views import APIView
from rest_framework import status

from rest_framework.response import Response
from spamapp.models import User,Contact,SpamReport
from django.conf import settings
from django.db.models import Q
from spamapp.middleware import CreateToken,CheckToken



# API to signup the application and returning the custom auth token to access other APIs
@api_view(["POST"])
def register_user(request):
    
    try:
        name = request.data.get('name')
        phone_number = request.data.get('phone_number')
        email = request.data.get('email', None)
        password = request.data.get('password')

        if not name or not phone_number or not password:
            return Response({"error": "Name, phone number, and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({"error": "Phone number already registered"}, status=status.HTTP_400_BAD_REQUEST)
        if email and User.objects.filter(email=email).exists():
            return Response({"error": "Email already registered"}, status=status.HTTP_400_BAD_REQUEST)
        hashed_password = make_password(password)

        # Create the user
        user = User(name=name, phone_number=phone_number, email=email, password=hashed_password)
        user.save()

        authToken=CreateToken(phone_number)

        return Response({"message": "User registered successfully","Token":authToken}, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

# API to login the application and returning the auth token to access other APIs
@api_view(["POST"])
def login_user(request):
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')
    authToken=CreateToken(phone_number)
    try:
        user = User.objects.get(phone_number=phone_number)
        
        if check_password(password, user.password):
            return Response({"message": "Login successful","Token":authToken}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Invalid password"}, status=status.HTTP_400_BAD_REQUEST)
        
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
    



# I am unsure whether the contacts was to be created for a user or not,
# but in the question it was mentioned that we need to do something with other member's contact list
# that's why I implemented create contact endpoint
@api_view(["POST"])
def create_contact(request):
    contact_name = request.data.get("contact_name")
    contact_phone_number = request.data.get("contact_phone_number")
    authfromheader = request.headers.get("Authorization")
    user = CheckToken(authfromheader)
    if user:
        try:
            contact_instance = Contact()
            contact_instance.contact_name = contact_name
            contact_instance.contact_phone_number = contact_phone_number
            contact_instance.created_by = user
            contact_instance.save()
            return Response({"Success":f'{contact_phone_number} is added in contacts'},status=status.HTTP_201_CREATED)
        except:
            return Response({"Error":"Bad Request"},status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)


# User can mark any number a spam, whether it is in contact list or any random number
@api_view(["POST"])
def spam_number(request):
    phone_number = request.data.get("phone_number")
    authfromheader = request.headers.get("Authorization")
    user = CheckToken(authfromheader)
    if user:
        try:
            spamInstance = SpamReport()
            spamInstance.phone_number = phone_number
            spamInstance.save()
            return Response({"Success":f'{phone_number} is added in spam'},status=status.HTTP_201_CREATED)
        except:
            return Response({"Error":"Bad Request"},status=status.HTTP_400_BAD_REQUEST)
    return Response({"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)


# API to get the list of users and based on the conditions and searching by name
# Returning the result with likelihood
@api_view(["GET"])
def get_by_name(request):
    authfromheader = request.headers.get("Authorization")
    user = CheckToken(authfromheader)
    query = request.GET.get('query', '')
    
    if user:
        if not query:
            return Response({"error": "Search query is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch users and contacts
        users_starting_with_name_query = User.objects.filter(name__istartswith=query).values('name', 'phone_number')
        users_containing_name_query = User.objects.filter(name__icontains=query).exclude(name__istartswith=query).values('name', 'phone_number')
        contacts_starting_with_name_query = Contact.objects.filter(contact_name__istartswith=query).values('contact_name', 'contact_phone_number')
        contacts_containing_name_query = Contact.objects.filter(contact_name__icontains=query).exclude(contact_name__istartswith=query).values('contact_name', 'contact_phone_number')
        
        combined_results = list(users_starting_with_name_query) + list(contacts_starting_with_name_query) + list(users_containing_name_query) + list(contacts_containing_name_query)
        
        results = []
        for entry in combined_results:
            phone_number = entry.get('phone_number') or entry.get('contact_phone_number')
            
            spam_likelihood = SpamReport.objects.filter(phone_number=phone_number).count()
            
            results.append({
                "name": entry.get('name') or entry.get('contact_name'),
                "phone_number": phone_number,
                "spam_likelihood": spam_likelihood,
            })
        
        return Response({"results": results}, status=status.HTTP_200_OK)

    return Response({"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)

# API to get the list of users and based on the conditions and searching by phonenumber
# Returning the result with likelihood
@api_view(["GET"])
def get_by_phone_number(request):
    authfromheader = request.headers.get("Authorization")
    user = CheckToken(authfromheader)
    phone_number = request.GET.get('phone_number', '')

    if user:
        if not phone_number:
            return Response({"error": "Phone number is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Search for a registered user with the exact phone number
        registered_user = User.objects.filter(phone_number=phone_number).values('name', 'phone_number', 'email').first()
        
        if registered_user:
            # Calculate spam likelihood for this registered user
            spam_likelihood = SpamReport.objects.filter(phone_number=phone_number).count()
            registered_user['spam_likelihood'] = spam_likelihood
            return Response({"result": registered_user}, status=status.HTTP_200_OK)
        
        # If no registered user, search through the contacts with the exact phone number
        contacts = Contact.objects.filter(contact_phone_number=phone_number).values('contact_name', 'contact_phone_number')
        
        if contacts.exists():
            results = []
            for contact in contacts:
                spam_likelihood = SpamReport.objects.filter(phone_number=contact['contact_phone_number']).count()
                results.append({
                    "name": contact['contact_name'],
                    "phone_number": contact['contact_phone_number'],
                    "spam_likelihood": spam_likelihood,
                })
            return Response({"results": results}, status=status.HTTP_200_OK)
        
        return Response({"error": "No results found"}, status=status.HTTP_404_NOT_FOUND)
    return Response({"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)



#api to get particular user details and with email and without email based on the conditions
@api_view(["GET"])
def get_user_details(request,phone_number):
    authfromheader = request.headers.get("Authorization")
    current_user = CheckToken(authfromheader)
    
    if current_user:
        # Check if the phone number belongs to a registered user
        registered_user = User.objects.filter(phone_number=phone_number).first()
        
        if registered_user:
            # Calculate spam likelihood for this phone number
            spam_likelihood = SpamReport.objects.filter(phone_number=phone_number).count()
            
            # Check if the current user is in the registered user's contact list
            is_in_contact_list = Contact.objects.filter(
                created_by=registered_user,
                contact_phone_number=current_user.phone_number
            ).exists()

             # Show email only if in contact list
            user_details = {
                "name": registered_user.name,
                "phone_number": registered_user.phone_number,
                "spam_likelihood": spam_likelihood,
                "email": registered_user.email if is_in_contact_list else None 
            }
            
            return Response({"result": user_details}, status=status.HTTP_200_OK)
        
        # If no registered user, check if the phone number exists in the contacts
        contact = Contact.objects.filter(contact_phone_number=phone_number).first()
        
        if contact:
            # Calculate spam likelihood for this phone number using the count method.
            spam_likelihood = SpamReport.objects.filter(phone_number=phone_number).count()

            # If the email is not shown for contacts
            contact_details = {
                "name": contact.contact_name,
                "phone_number": contact.contact_phone_number,
                "spam_likelihood": spam_likelihood,
                "email": None  
            }
            
            return Response({"result": contact_details}, status=status.HTTP_200_OK)
        
        return Response({"error": "No details found for the provided phone number"}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({"error": "User not found"}, status=status.HTTP_401_UNAUTHORIZED)


    

