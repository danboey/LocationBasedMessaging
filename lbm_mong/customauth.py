from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest, Unauthorized
from models import Person

        
class CustAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        user = request.GET.get('user_id') or request.POST.get('user_id')
        api_key = request.GET.get('api_key') or request.POST.get('api_key')
        #name = request.GET.get('username') or request.POST.get('username')
        try:
            test = Person.objects(user_id=user)
            print test
        except:
            return False
        if Person.objects(user_id=user, api_key=api_key):
            return True
        return False
        
        
        
