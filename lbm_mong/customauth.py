from tastypie.authentication import Authentication
from models import MyUser

        
class CustAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        user = request.GET.get('user_id') or request.POST.get('user_id')
        api_key = request.GET.get('api_key') or request.POST.get('api_key')
        try:
            '''check user exists'''
            test = MyUser.objects(user_id=user)
            print test
        except:
            return False
        '''check user_id and api_key is a valid combination'''
        if MyUser.objects(user_id=user, api_key=api_key):
            return True
        return False
        
        
        
