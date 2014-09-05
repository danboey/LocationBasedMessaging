'''Import for push notifications'''
#from pyapns import configure, provision, notify
#from lbm_mong.models import MyUser


from tastypie.exceptions import BadRequest
from bson import json_util
import json   
import random
import string
import binascii


'''Sends a silent push notification to the receiver to notify the application of a new message. 
   Has been commented out since push notfications can't be tested without a client side app.'''
'''def send_push(sender, document, **kwargs):
       receiver_id = document['receiver_id']
       receiver = MyUser.objects.get(user_id= receiver_id)
       apns_token = receiver.apns_token

       notification = [
       { aps = {"content-available" = 1; sound = "";};}
       ]

       configure({'HOST': 'https://dlmb.uk/'})
       provision('myapp', open('cert.pem').read(), 'production')
       notify('myapp', apns_token, notification)'''


'''This simply shows how push notification could be triggered by a signal after message is POSTed.
   As detailed above, real push notifications can't be tested without a client side app.'''
def send_push(sender, document, **kwargs):
    print "PUSH NOTIFICATION TO RECIPIENT"
    

'''Generates random token of variable length (between 20 and 30 characters),
   including upper/lower case and digits. Stored in db as user's API access token.
   Token is required (along with user_id) for subsequent calls to the API.'''
def generate_random_token(sender, document, **kwargs):
    '''Check whether api_key already exists - to avoid creating a new one when client PATCHes apns_token field'''
    if document.api_key == '':
        size = random.randrange(20, 30, 1)
        character_set = string.ascii_uppercase + string.ascii_lowercase + string.digits 
        token = ''.join(random.SystemRandom().choice(character_set) for _ in range(size))
        document.api_key = token
    
 

        
        

