from django.contrib.auth.hashers import make_password,check_password
from spamapp.models import User

def CreateToken(phone_number):
    authToken=make_password(phone_number)
    print(check_password(phone_number,authToken))
    return authToken

def CheckToken(token):
    allUsers = User.objects.all()
    for user in allUsers:
        if(check_password(user.phone_number,token)):
            return user
    return False


