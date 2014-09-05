from django.conf.urls import patterns, include, url
from tastypie_mongoengine import resources
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from customauth import CustAuthentication
from mongoengine import *
from mongoengine.django.auth import User
from models import Message, MyUser, Friends
from social.apps.django_app.utils import load_strategy
from social.backends.utils import load_backends
from tastypie.exceptions import NotRegistered, BadRequest, Unauthorized, NotFound
from functions import check_user_id_sending, check_user_id_updating, check_receiver, get_friends, check_bundle_data, delete_meta, set_update, send_email
import urllib2
import json
from bson import json_util
        
'''Tastypie Resources - defining the API'''
        
'''Resource for sending messages'''                
class MessageResource(resources.MongoEngineResource):
        
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'messages'
        fields = ['id', 'user_id', 'content', 'recipient_id', 'date_sent', 'received', 'date_received', 'location']
        allowed_methods = ['post', 'patch']
        authentication = CustAuthentication()
        authorization = Authorization()
        allowed_update_fields = ['received', 'pushed']
        always_return_data = True
    
    '''Called when POSTing new msg. Checks sent data then checks receiver exists and is on
       user's friends list before creating new Message object'''
    def obj_create(self, bundle, **kwargs):
        check_bundle_data(bundle)
        if not check_receiver(bundle):
            raise BadRequest("Recipient ID not valid or not in friends list")
        if not check_user_id_sending(bundle):
            raise BadRequest("Unauthorised - 'user_id' in payload incorrect")
        return super(MessageResource, self).obj_create(bundle, **kwargs)
                      
    '''PATCH request - checks that only received or pushed fields being updated.
       super() eventually calls obj_update (overridden below)'''        
    def update_in_place(self, request, original_bundle, new_data):
        if set(new_data.keys()) - set(self._meta.allowed_update_fields):
            raise BadRequest("Only the 'received' and 'pushed' boolean fields can be updated")
        return super(MessageResource, self).update_in_place(request, original_bundle, new_data)
         
    '''Called by update_in_place - overridden to check authorizations before updating object'''
    def obj_update(self, bundle, request = None, **kwargs):
        '''check that requesting user is the recipient of the message'''
        if not check_user_id_updating(bundle, **kwargs):
            raise BadRequest("Unauthorised")
        '''check that update values in payload are valid (only allow updating to true)'''
        if bundle.data['received'] != True and bundle.data['pushed'] != True:
            raise BadRequest("Invalid - received/pushed fields can only be updated to 'true'")
        set_update(bundle)  
        
    '''Exclude 'meta' information in response'''    
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict)
        
                
                
'''Resource for accessing sent messages'''                        
class SentMessageResource(resources.MongoEngineResource):
        
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'sent_messages'
        fields = ['id', 'content', 'recipient_id', 'date_sent', 'received', 'date_received', 'location']
        allowed_methods = ['get']
        authentication = CustAuthentication()
        authorization = Authorization()
        always_return_data = True
        max_limit = 50      

    '''Depending on URL params, user can GET list of all sent msgs or only msgs 
       that have either been/not been received'''
    def obj_get_list(self, bundle, **kwargs):
        user = bundle.request.GET.get('user_id') #extracts user_id from URL params
        if bundle.request.GET.get('received'):
            received = False if bundle.request.GET.get('received') == "false" else True
            return Message.objects(user_id=user, received=received)
        else:
            return Message.objects(user_id=user)
    
    '''Returns single sent message'''    
    def obj_get(self, bundle, request=None, **kwargs):
        return super(SentMessageResource, self).obj_get(bundle, **kwargs)



'''Resource for accessing received messages'''                
class ReceivedMessageResource(resources.MongoEngineResource):
        
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'received_messages'
        fields = ['id', 'content', 'user_id', 'date_sent', 'date_received', 'location']
        allowed_methods = ['get']
        authentication = CustAuthentication()
        authorization = Authorization()
        always_return_data = True       

    '''Only returns msgs that have actually been received by the user (as opposed to
       msgs sent to the client app, ie. msgs stored locally but not yet seen by user)'''
    def obj_get_list(self, bundle, **kwargs):
        user = bundle.request.GET.get('user_id')
        return Message.objects(recipient_id=user, received=True)
        
    def obj_get(self, bundle, request=None, **kwargs):
        msg_id = kwargs['pk'] #extracts Message object ID from URI
        user = bundle.request.GET.get('user_id')
        try:
            return Message.objects.get(id=msg_id, recipient_id=user, received=True)
        except:
            raise BadRequest
             
        
        
'''Resource for retrieving new messages in response to push notifications'''          
class PullMessageResource(resources.MongoEngineResource):
      
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'pull_messages'
        fields = ['id', 'content', 'user_id', 'date_sent', 'received', 'location']
        allowed_methods = ['get']
        authentication = CustAuthentication()
        authorization = Authorization()
        always_return_data = True       

    '''Returns list of all new messages - ie. where pushed=false'''
    def obj_get_list(self, bundle, **kwargs):
        user = bundle.request.GET.get('user_id')
        return Message.objects(recipient_id=user, pushed=False)
  
    def obj_get(self, bundle, request=None, **kwargs):
        raise BadRequest("Unauthorised - use /api/messages/pull_message/ to retrieve list of all new messages")
       
                

'''Resource for authenticating new users via facebook using python-social-auth'''
class SocialSignUpResource(resources.MongoEngineResource):
    
    class Meta:
        queryset = MyUser.objects.all()
        allowed_methods = ['post', 'get', 'patch']
        authentication = Authentication()
        authorization = Authorization()
        resource_name = "users"
        fields = ['id', 'username', 'api_key', 'user_id', 'access_token', 'first_name', 'last_name', 'date_joined', 'last_login', 'email', 'apns_token']
        allowed_update_fields = ['apns_token']
        always_return_data = True

    def obj_create(self, bundle, request=None, **kwargs):
        access_token = bundle.data['access_token']
        strategy = load_strategy(backend='facebook')
        try:
            user = strategy.backend.do_auth(access_token)
            user_id = user['id']
            MyUser.objects(id=user_id).update(set__access_token=access_token)
        except:
            raise BadRequest("Error [1] authenticating user with this provider")
        if user and user.is_active:
            '''Populates friends list via call to facebook API'''
            get_friends(user)
            bundle.obj = user
            rtn_data = MyUser.objects.get(id=user_id)
            bundle.obj.user_id, bundle.obj.access_token = rtn_data.user_id, rtn_data.access_token
            return bundle
        else:
            raise BadRequest("Error [2] authenticating user with this provider")
            
    '''Since Authentication() is used in this class (which doesn't check any credentials - necessary for obj_create 
        method), proper authentication and authorization needs to be checked before returning MyUser object'''        
    def obj_get(self, bundle, **kwargs):
        get_user = kwargs['pk']
        user_id = bundle.request.GET.get('user_id')
        api_key = bundle.request.GET.get('api_key')
        '''authenticates and checks that the user is accessing the correct endpoint'''
        try:
            user = MyUser.objects.get(user_id=user_id, api_key=api_key)
            if str(user.id) == str(get_user):
                return user
            else:
                raise BadRequest("User does not exist/wrong auth credentials")
        except:
            raise BadRequest("User does not exist/wrong auth credentials")
       
    def obj_get_list(self, bundle, **kwargs):
        user_id = bundle.request.GET.get('user_id')
        api_key = bundle.request.GET.get('api_key')
        user = MyUser.objects(user_id=user_id, api_key=api_key)
        return user    
                
    def update_in_place(self, request, original_bundle, new_data):
        if set(new_data.keys()) - set(self._meta.allowed_update_fields):
            raise BadRequest("Update apns_token field only")
        return super(SocialSignUpResource, self).update_in_place(request, original_bundle, new_data)
        
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict) 
           
                        
        
'''Resource for sending email recommendation to non-users'''                
class EmailRecommendationResource(resources.MongoEngineResource):
    
    class Meta:
        queryset = MyUser.objects.all()
        allowed_methods = ['get', 'post']
        authentication = CustAuthentication()
        authorization = Authorization()
        fields = ['user_id', 'email_recommendations']
        resource_name = "email_recommendations" 
             
    def obj_create(self, bundle, **kwargs):
        user_id = bundle.request.GET.get('user_id')
        send_to = bundle.data['email']
        send_email(user_id, send_to)
              
    def obj_get_list(self, bundle, **kwargs):
        user_id = bundle.request.GET.get('user_id')
        return MyUser.objects(user_id=user_id)
             
    def obj_get(self, bundle, **kwargs):
        raise BadRequest("Unauthorized - you can only retreive a list of previous recommendations")
              
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict) 
        

        
        
'''Resource for accessing list of user's friends who are also registered to use the app'''        
class FriendsResource(resources.MongoEngineResource):

    class Meta:
        queryset = Friends.objects.all()
        allowed_methods = ['get']
        fields = ['friends']
        authentication = CustAuthentication()
        authorization = Authorization()
        resource_name = "friends"
        always_return_data = True
        
    def obj_get_list(self, bundle, **kwargs):
        user_id = bundle.request.GET.get('user_id')
        user = MyUser.objects.get(user_id=user_id)
        username = user.username
        '''update friends list first'''
        get_friends(username)
        return Friends.objects(user_id=user_id)
        
    def obj_get(self, bundle, **kwargs):
        return super(FriendsResource, self).obj_get(bundle, **kwargs)
                    
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict)
            
            
            
        
