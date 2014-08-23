from lbm_mong.models import Person, Friends, Message
from rec_email import recommendation_email
from tastypie.exceptions import BadRequest
from datetime import datetime
import urllib2
import json

'''Authorization for sending message'''
def check_user_id_sending(bundle, **kwargs):
    user = bundle.request.GET.get('user_id')
    sender = bundle.data['user_id']
    if user == sender:
        return True
    return False
    
'''Authorisation - checks that requesting user is the recipient of the message'''
def check_user_id_updating(bundle, **kwargs):
    user = bundle.request.GET.get('user_id')
    recipient = bundle.obj.recipient_id
    if user == recipient:
        return True
    return False
    
    
def check_receiver(bundle, **kwargs):
    receiver = bundle.data['recipient_id']
    sender = bundle.data['user_id']
    '''Check recipient exists'''
    if not Person.objects(user_id=receiver):
        return False
    '''Check recipient is in user's friends list'''
    friends_list = Friends.objects.get(user_id=sender)
    for friend in friends_list.friends:
        if friend['id'] == receiver:
            return True
    return False
            
def check_bundle_data(bundle, **kwargs):
    try:
        bundle.data['user_id']
        bundle.data['recipient_id']
        return
    except:
        raise BadRequest("Required field(s) missing")
        

'''When client app receives the message, the app should send a patch to update the 'pushed' field to true.
   When in range of location and client app notifies user of message, app should send PATCH to update
   received field to true. date_received field is then set to current datetime.'''
def set_update(bundle, **kwargs):
    msg_id = bundle.obj.id
    msg = Message.objects.get(id=msg_id)
    if msg.pushed == False and bundle.data['pushed'] == True:
        Message.objects.get(id=msg_id).update(set__pushed=True)
    elif msg.pushed == True and msg.received == False and bundle.data['received'] == True:
        Message.objects.get(id=msg_id).update(set__received=True)
        Message.objects.get(id=msg_id).update(set__date_received=datetime.now())
    else:
        raise BadRequest("Invalid update")

    
def get_friends(user):
    name = Person.objects.get(username=str(user))
    access_token, uid = name.access_token, name.user_id 
    url = u"https://graph.facebook.com/%s/friends?access_token=%s" % (uid, access_token)
    request = urllib2.Request(url)
    friends = json.loads(urllib2.urlopen(request).read()).get('data')
    if not Friends.objects(user_id=uid):
        new = Friends(user_id=uid, friends=friends)
        new.save()
    else:
        Friends.objects(user_id=uid).update(set__friends=friends)
        
        
                
def send_email(user_id, email):
    user = Person.objects.get(user_id=user_id)
    email_recs = user.email_recommendations
    print email_recs
    if email in email_recs:
        raise BadRequest("A recommendation has already been sent to the given email address")
    if not Person.objects(email=email):
        email_recs.append(email)
        #add the email address to the email_recommendations list and update the resource
        Person.objects.get(user_id=user_id).update(set__email_recommendations=email_recs)
        recommendation_email(user, email)
        return
    else:
        raise BadRequest("%s is already a registered user!"% email)         

        
        
'''Remove meta information from some responses'''
def delete_meta(self, data_dict, dict):
    if isinstance(data_dict, dict): 
        if 'meta' in data_dict: 
            del(data_dict['meta']) 
        return data_dict 
        
