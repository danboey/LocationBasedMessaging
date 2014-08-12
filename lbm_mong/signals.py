from rec_email import recommendation_email
from bson import json_util
import json   
import random
import string
import binascii
import urllib2
import social_auth


'''Send push notification after message is saved, by triggering signal. Not yet implemented.
   This simply shows how push notification could be triggered after message is POSTed'''
def send_push(sender, document, **kwargs):
    push_msg = {}
    push_msg['id'] = document['id']
    push_msg['date_sent'] = document['date_sent']
    json_data = json.dumps(push_msg, default=json_util.default)
    print json_data
    


'''Generates random token of variable length (between 20 and 30 characters),
   including upper/lower case and digits. Stored in db as user's API access token.
   Token is required (along with username) for subsequent calls to the API.'''
def generate_random_token(sender, document, **kwargs):
    size = random.randrange(20, 30, 1)
    character_set = string.ascii_uppercase + string.ascii_lowercase + string.digits 
    token = ''.join(random.SystemRandom().choice(character_set) for _ in range(size))
    document.api_token = token
    

'''Allows user to send email recommending application to friends'''    
def send_email(sender, document, **kwargs):
    recommendation_email(document)    
    
def get_friends(user):
    from lbm_mong.models import Person, Test
    name = Person.objects(username=str(user))
    for data in name:
        for key in data:
            if key == 'access_token':
                access_token = data[key]
            if key == 'uid':
                uid = data[key]
    url = u"https://graph.facebook.com/%s/friends?access_token=%s" % (uid, access_token)
    print url
    request = urllib2.Request(url)
    friends = json.loads(urllib2.urlopen(request).read()).get('data')
    print friends
    if not Test.objects(uid=uid):
        new = Test(uid=uid, friends=friends)
        new.save()



