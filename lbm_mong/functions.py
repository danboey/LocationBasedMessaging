from lbm_mong.models import Person, Friends
from tastypie.exceptions import BadRequest
import urllib2
import json

def check_user_id(bundle, **kwargs):
    user = bundle.request.GET.get('user_id')
    sender = bundle.data['user_id']
    if user == sender:
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
        
