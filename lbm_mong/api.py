from django.conf.urls import patterns, include, url
from tastypie_mongoengine import resources
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from customauth import CustAuthentication
from mongoengine.django.auth import User
from models import Message, Person, EmailRecommendations, Friends
from social.apps.django_app.utils import load_strategy
from social.backends.utils import load_backends
from tastypie.exceptions import NotRegistered, BadRequest, Unauthorized, NotFound
from functions import check_user_id_sending, check_user_id_updating, check_receiver, get_friends, check_bundle_data, delete_meta, set_update
import urllib2
import json
        
        
class MessageResource(resources.MongoEngineResource):
        
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'messages'
        fields = ['id', 'user_id', 'content', 'recipient_id', 'date_sent', 'received', 'date_received', 'pushed', 'location']
        allowed_methods = ['post', 'patch']
        authentication = CustAuthentication()
        authorization = Authorization()
        always_return_data = True
        allowed_update_fields = ['received', 'pushed']
    
    def obj_create(self, bundle, **kwargs):
        check_bundle_data(bundle)
        if not check_receiver(bundle):
            raise BadRequest("Recipient ID not valid or not in friends list")
        if not check_user_id_sending(bundle):
            raise BadRequest("Unauthorised - 'user_id' in payload incorrect")
        return super(MessageResource, self).obj_create(bundle, **kwargs)
        
    def obj_update(self, bundle, request = None, **kwargs):
        #check that requesting user is the recipient of the message
        if not check_user_id_updating(bundle, **kwargs):
            raise BadRequest("Unauthorised")
        #check that update values are valid
        if bundle.data['received'] != True and bundle.data['pushed'] != True:
            raise BadRequest("Invalid - received/pushed fields can only be updated to 'true'")
        set_update(bundle)
            
    '''PATCH request - to change 'received' or 'pushed' boolean fields from false to true. 
       Only 'received' and 'pushed' fields can be updated'''        
    def update_in_place(self, request, original_bundle, new_data):
        if set(new_data.keys()) - set(self._meta.allowed_update_fields):
            raise BadRequest("Only the 'received' and 'pushed' boolean fields can be updated")
        return super(MessageResource, self).update_in_place(request, original_bundle, new_data)  
        
    '''Exclude 'meta' information in response'''    
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict)
        
                
                
                
class SentMessageResource(resources.MongoEngineResource):
        
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'sent_messages'
        fields = ['id', 'content', 'recipient_id', 'date_sent', 'received', 'date_received']
        allowed_methods = ['get']
        authentication = CustAuthentication()
        authorization = Authorization()
        always_return_data = True
        #max_limit = None       

    def obj_get_list(self, bundle, **kwargs):
        '''Depending on URL params, user can GET list of all sent msgs or only msgs 
           that have either been/not been received'''
        user = bundle.request.GET.get('user_id')
        if bundle.request.GET.get('received') == "true":
            msgs = Message.objects(user_id=user, received=True)
        elif bundle.request.GET.get('received') == "false":
            msgs = Message.objects(user_id=user, received=False)
        else:
            msgs = Message.objects(user_id=user)
        return msgs
        
    def obj_get(self, bundle, request=None, **kwargs):
        msg_id = kwargs['pk']
        user = bundle.request.GET.get('user_id')
        msg = self.get_object_list(request).filter(id=msg_id, user_id=user)
        try:
            if len(msg) == 0:
                pass
            return msg[0]
        except:
            raise BadRequest("The message does not exist")
        
        
class ReceivedMessageResource(resources.MongoEngineResource):
        
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'received_messages'
        fields = ['id', 'content', 'user_id', 'date_sent', 'date_received']
        allowed_methods = ['get']
        authentication = CustAuthentication()
        authorization = Authorization()
        always_return_data = True       

    def obj_get_list(self, bundle, **kwargs):
        '''Only returns msgs that have actually been received by the user (as opposed to
           msgs sent to the client app, ie. msgs stored locally but not yet seen by user)'''
        user = bundle.request.GET.get('user_id')
        msgs = Message.objects(recipient_id=user, received=True)
        return msgs
        
    def obj_get(self, bundle, request=None, **kwargs):
        msg_id = kwargs['pk']
        user = bundle.request.GET.get('user_id')
        msg = self.get_object_list(request).filter(id=msg_id, recipient_id=user, received=True)
        try:
            if len(msg) == 0:
                pass
            return msg[0]
        except:
            raise BadRequest("The message does not exist or has not yet been received by the user")
             
        
        
'''When a push notification is received the client app should use this end-point to GET the msg'''          
class PullMessageResource(resources.MongoEngineResource):
      
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'pull_message'
        fields = ['id', 'content', 'user_id', 'date_sent', 'recipient_id', 'received']
        allowed_methods = ['get']
        authentication = CustAuthentication()
        authorization = Authorization()
        always_return_data = True       

    def obj_get_list(self, bundle, **kwargs):
        user = bundle.request.GET.get('user_id')
        msgs = Message.objects(recipient_id=user, received=False)
        return msgs
        
    def obj_get(self, bundle, request=None, **kwargs):
        user = bundle.request.GET.get('user_id')
        msg_id = kwargs['pk']
        msg = self.get_object_list(request).filter(id=msg_id, recipient_id=user, received=False)
        try:
            if len(msg) == 0:
                pass
            return msg[0]
        except:
            raise BadRequest("Either message already received by recipient, msg ID does not exist or you are not the intended recipient for this message")

        
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict)
       
                

'''Authenticate users via facebook using python-social-auth'''
class SocialSignUpResource(resources.MongoEngineResource):
    
    class Meta:
        queryset = Person.objects.all()
        allowed_methods = ['post', 'get']
        authentication = Authentication()
        authorization = Authorization()
        resource_name = "users"
        fields = ['id', 'username', 'api_key']
        always_return_data = True

    def obj_create(self, bundle, request=None, **kwargs):
        access_token = bundle.data['access_token']
        strategy = load_strategy(backend='facebook')
        try:
            user = strategy.backend.do_auth(access_token)
            user_id = user['id']
            Person.objects(id=user_id).update(set__access_token=access_token)
        except:
            raise BadRequest("Error [1] authenticating user with this provider")
        if user and user.is_active:
            '''Populates friends list via call to facebook API'''
            get_friends(user, user_id)
            bundle.obj = user
            print "END"
            return bundle
        else:
            raise BadRequest("Error [2] authenticating user with this provider")
            
    def obj_get(self, bundle, **kwargs):
        get_user = kwargs['pk']
        user = bundle.request.GET.get('user_id')
        '''check that the authenticated user is accessing the correct endpoint'''
        if get_user == user:
            return Person.objects.get(user_id=user)
        else:
            raise BadRequest("Unauthorized - wrong URI for authenticated user")
       
    def obj_get_list(self, bundle, **kwargs):
        raise BadRequest("Unauthorized - use '/api/users/{userID}' endpoint")
                       
  

'''End-point for sending email recommendation to user's friends, email address must be supplied'''
class EmailRecommendationResource(resources.MongoEngineResource):
    
    class Meta:
        queryset = EmailRecommendations.objects.all()
        allowed_methods = ['get', 'post']
        fields = ['email', 'user_id']
        authentication = CustAuthentication()
        authorization = Authorization()
        resource_name = "recommend"
        
    def obj_get_list(self, bundle, **kwargs):
        user = bundle.request.GET.get('user_id')
        sent_list = EmailRecommendations.objects(user_id=user)
        return sent_list
        
    def obj_get(self, bundle, **kwargs):
        raise BadRequest("Unauthorized - you can only retreive a list of previous recommendations")
        
    def obj_create(self, bundle, **kwargs):
        return super(EmailRecommendationResource, self).obj_create(bundle, **kwargs)
        
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict)
        
        
'''Endpoint for accessing list of user's friends who are also registered to use the app'''        
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
        user = Person.objects.get(user_id=user_id)
        username = user.username
        '''update friends list first'''
        get_friends(username)
        return Friends.objects(user_id=user_id)
        
    def obj_get(self, bundle, **kwargs):
        raise BadRequest("Unauthorised - use '/api/friends/' endpoint")
        
            
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict)
            
            
            
        
