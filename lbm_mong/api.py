from tastypie_mongoengine import resources
from tastypie.authorization import Authorization
from tastypie.authentication import Authentication
from customauth import CustAuthentication
from mongoengine.django.auth import User
from models import Message, Person, EmailRecommendations, Friends
from social.apps.django_app.utils import load_strategy
from social.backends.utils import load_backends
from tastypie.exceptions import NotRegistered, BadRequest, Unauthorized
from signals import get_friends
import urllib2
import json


def delete_meta(self, data_dict, dict):
    if isinstance(data_dict, dict): 
        if 'meta' in data_dict: 
            del(data_dict['meta']) 
        return data_dict 
        
        
class MessageResource(resources.MongoEngineResource):
        
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'messages'
        fields = ['id', 'message', 'recipient', 'username', 'date_sent', 'received']
        allowed_methods = ['post', 'patch']
        authentication = CustAuthentication()
        authorization = Authorization()
        always_return_data = True
        allowed_update_fields = ['received']
    
    def obj_create(self, bundle, **kwargs):
        try:
            bundle.data['recipient']
        except:
            raise BadRequest("The 'recipient' field has no data and doesn't allow a default or null value")
        intended_recipient = bundle.data["recipient"]
        if not Person.objects(username=intended_recipient):
            raise BadRequest("Recipient is not a registered user")
        return super(MessageResource, self).obj_create(bundle, **kwargs)
            
    def obj_update(self, bundle, **kwargs):
        user = bundle.request.GET.get('username')
        intended_recipient = bundle.obj.recipient
        '''Check if user is the intended recipient of the message'''
        if user == intended_recipient:
            return self.obj_create(bundle, **kwargs)
        raise BadRequest("You are not the intended recipient for this message")   
            
    '''PATCH request - to change 'received' boolean field from false to true once the user
       actually opens the message. Only 'received' field can be updated'''        
    def update_in_place(self, request, original_bundle, new_data):
        if set(new_data.keys()) - set(self._meta.allowed_update_fields):
            raise BadRequest("Only the 'received' field can be updated")
        return super(MessageResource, self).update_in_place(request, original_bundle, new_data)  
        
    '''Exclude 'meta' information in response'''    
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict)
        
                
                
                
class SentMessageResource(resources.MongoEngineResource):
        
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'sent_msgs'
        fields = ['id', 'message', 'recipient', 'date_sent', 'received']
        allowed_methods = ['get']
        authentication = CustAuthentication()
        authorization = Authorization()
        always_return_data = True       

    def obj_get_list(self, bundle, **kwargs):
        '''Depending on URL params, user can GET list of all sent msgs or only msgs 
           that have either been/not been received'''
        user = bundle.request.GET.get('username')
        if bundle.request.GET.get('received') == "true":
            msgs = Message.objects(username=user, received=True)
        elif bundle.request.GET.get('received') == "false":
            msgs = Message.objects(username=user, received=False)
        else:
            msgs = Message.objects(username=user)
        return msgs
        
    def obj_get(self, bundle, request=None, **kwargs):
        msg_id = kwargs['pk']
        user = bundle.request.GET.get('username')
        msg = self.get_object_list(request).filter(id=msg_id, username=user)
        try:
            if len(msg) == 0:
                pass
            return msg[0]
        except:
            raise BadRequest("The message does not exist")
        
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict)
        
        
class ReceivedMessageResource(resources.MongoEngineResource):
        
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'received_msgs'
        fields = ['id', 'message', 'username', 'date_sent', 'recipient', 'received']
        allowed_methods = ['get']
        authentication = CustAuthentication()
        authorization = Authorization()
        always_return_data = True       

    def obj_get_list(self, bundle, **kwargs):
        '''Only returns msgs that have actually been received by the user (as opposed to
           msgs sent to the client app, ie. msgs stored locally but not yet seen by user)'''
        user = bundle.request.GET.get('username')
        msgs = Message.objects(recipient=user, received=True)
        return msgs
        
    def obj_get(self, bundle, request=None, **kwargs):
        msg_id = kwargs['pk']
        user = bundle.request.GET.get('username')
        msg = self.get_object_list(request).filter(id=msg_id, recipient=user, received=True)
        try:
            if len(msg) == 0:
                pass
            return msg[0]
        except:
            raise BadRequest("The message does not exist or has not yet been received by the user")
             
        
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict)
      
      
        
'''When a push notification is received the client app should use this end-point to GET the msg'''          
class PullMessageResource(resources.MongoEngineResource):
      
    class Meta:
        queryset = Message.objects.all()
        resource_name = 'pull_msg'
        fields = ['id', 'message', 'username', 'date_sent', 'recipient', 'received']
        allowed_methods = ['get']
        authentication = CustAuthentication()
        authorization = Authorization()
        always_return_data = True       

    def obj_get_list(self, bundle, **kwargs):
        user = bundle.request.GET.get('username')
        msgs = Message.objects(recipient=user, received=False)
        return msgs
        
    def obj_get(self, bundle, request=None, **kwargs):
        user = bundle.request.GET.get('username')
        msg_id = kwargs['pk']
        msg = self.get_object_list(request).filter(id=msg_id, recipient = user, received=False)
        try:
            if len(msg) == 0:
                pass
            return msg[0]
        except:
            raise BadRequest("Either message already received by recipient, msg id does not exist or you are not the intended recipient for this message")

        
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict)
       
                

'''Authenticate users via facebook using python-social-auth'''
class SocialSignUpResource(resources.MongoEngineResource):
    
    class Meta:
        queryset = Person.objects.all()
        allowed_methods = ['post']
        authentication = Authentication()
        authorization = Authorization()
        resource_name = "users"
        fields = ['id', 'username', 'api_token']
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
                       
  

'''End-point for sending email recommendation to user's friends, email address must be supplied'''
class EmailRecommendationResource(resources.MongoEngineResource):
    
    class Meta:
        queryset = EmailRecommendations.objects.all()
        allowed_methods = ['get', 'post']
        fields = ['email', 'username']
        authentication = CustAuthentication()
        authorization = Authorization()
        resource_name = "recommend"
        
    def obj_get_list(self, bundle, **kwargs):
        user = bundle.request.GET.get('username')
        sent_list = EmailRecommendations.objects(username=user)
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
        
    def obj_get_list(self, bundle, **kwargs):
        '''update friends list first'''
        username = bundle.request.GET.get('username')
        user = Person.objects.get(username=username)
        user_uid = user.uid
        get_friends(username, user_uid)
        friends = Friends.objects(uid=user_uid)
        return friends
            
    def alter_list_data_to_serialize(self, request, data_dict): 
        return delete_meta(self, data_dict, dict)
            
            
            
        
