from datetime import datetime
from mongoengine.django.auth import User
from mongoengine import *
from mongoengine import signals
from signals import send_push, generate_random_token

class Message(Document):
    user_id = StringField(required=True)
    recipient_id = StringField(required=True)
    content = StringField(required=True)
    date_sent = DateTimeField(default=datetime.now)
    pushed = BooleanField(default=False)
    received = BooleanField(default=False)
    date_received = DateTimeField(required=False)
    location = PointField(required=True)
    meta = {
        'indexes': ['user_id']
    }

    def __unicode__(self):
        return self.user_id

    def save(self, *args, **kwargs):
        return super(Message, self).save(*args, **kwargs)

signals.post_save.connect(send_push, sender=Message)

'''Extends mongoengine.django.auth User model to include API key, access token, apns_token, email and facebook user_id    
   fields'''
class MyUser(User):
    api_key = StringField(default='')
    access_token = StringField(default='')
    apns_token = StringField(default='')
    email = EmailField(unique=True)
    user_id = StringField(default='')
    email_recommendations = ListField(default=[]) 
    meta = {
        'indexes': ['user_id']
    }

signals.pre_save.connect(generate_random_token, sender=MyUser)                             


'''Stores friends lists'''
class Friends(Document):
    user_id = StringField(default='')
    friends = ListField(default=[])
    meta = {
        'indexes': ['user_id']
    }




        
