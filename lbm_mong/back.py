from django.conf import settings
from django.contrib.auth.models import check_password
from models import Person

class PersonAuthBackend(object): 

    def authenticate(self, username=None, password=None): 
        user = Person.objects(username=username.lower()).first() 
        if user: 
            if password and user.check_password(password): 
                return user 
        return None 

    def get_user(self, username): 
        return Person.objects.with_id(username) 
