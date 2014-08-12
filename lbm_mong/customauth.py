from tastypie.authentication import Authentication
from tastypie.authorization import Authorization
from tastypie.exceptions import BadRequest, Unauthorized
from models import Person

'''Custom class for handling authentication.
   User must provide username and api_token with request.'''
'''class CustAuthentication(Authentication):
    def is_authenticated(self, request, **kwargs):
        user = request.GET.get('id') or request.POST.get('id')
        api_key = request.GET.get('api_key') or request.POST.get('api_key')
        if Person.objects(id=user, api_token=api_key):
            return True
        return False'''
        
        
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
        
        
        
        
        
        
        
        
        
        
        
        
        
        

'''class CustAuthorisation(Authorization):
    def read_list(self, object_list, bundle):
        return object_list.filter(user=bundle.request.username)

    def read_detail(self, object_list, bundle):
        if bundle.obj.username == bundle.request.GET.get('username'):
            print "Request username == sender"
            return True
        elif bundle.obj.recipient == bundle.request.GET.get('username') and bundle.obj.received == True:
            print "Request username == reciever AND received = True"
            return True
        return bundle.obj.recipient == bundle.request.GET.get('username')
        
    def create_list(self, object_list, bundle):
        return object_list

    def create_detail(self, object_list, bundle):
        #print bundle.obj.username #(username in data)
        #print bundle.request.GET.get('username') #(username in url)
        #Check if recipient is registered user
        receiver = bundle.obj.recipient
        if not Person.objects(username=receiver):
            raise BadRequest("Recipient does not exist")
        return bundle.obj.username == bundle.request.GET.get('username')

    def update_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no list-updates")
    
    #Patch (to update 'received' field) can only be done if user is the intended recipient of the msg
    def update_detail(self, object_list, bundle):
        return bundle.obj.recipient == bundle.request.GET.get('username')

    def delete_list(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")

    def delete_detail(self, object_list, bundle):
        raise Unauthorized("Sorry, no deletes.")'''
