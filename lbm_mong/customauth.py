from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest, Unauthorized
from models import Person

        
class CustAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        user = request.GET.get('id') or request.POST.get('id')
        api_key = request.GET.get('api_key') or request.POST.get('api_key')
        name = request.GET.get('username') or request.POST.get('username')
        try:
            test = Person.objects(id=user)
            print test
        except:
            return False
        if Person.objects(id=user, username=name, api_token=api_key):
            return True
        return False
        
        
        
