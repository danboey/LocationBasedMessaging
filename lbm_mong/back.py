from django.conf import settings
from django.contrib.auth.models import check_password
from models import MyUser

'''Custom Authentication backend'''
class MyUserAuthBackend(object): 

    def authenticate(self, username=None, password=None): 
        user = MyUser.objects(username=username.lower()).first() 
        if user: 
            if password and user.check_password(password): 
                return user 
        return None 

    def get_user(self, username): 
        return MyUser.objects.with_id(username) 
