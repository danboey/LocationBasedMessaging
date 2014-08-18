from datetime import datetime
from mongoengine.django.auth import User
from mongoengine import *
from mongoengine import signals
from signals import send_push, generate_random_token, send_email

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
        return self.username

    def save(self, *args, **kwargs):
        return super(Message, self).save(*args, **kwargs)

signals.post_save.connect(send_push, sender=Message)

'''Extends mongoengine.django.auth User model to include API key, access token, email and facebook uid fields'''
class Person(User):
    api_key = StringField(default='')
    access_token = StringField(default='') #new
    email = EmailField(unique=True)
    user_id = StringField(default='')
    meta = {
        'indexes': ['user_id']
    }

signals.pre_save.connect(generate_random_token, sender=Person)                             



class EmailRecommendations(Document):
    email = EmailField(required=True)
    user_id = StringField(required=True)
    meta = {
        'indexes': ['user_id']
    }

    def __unicode__(self):
        return self.user_id

    def save(self, *args, **kwargs):
        return super(EmailRecommendations, self).save(*args, **kwargs)

signals.post_save.connect(send_email, sender=EmailRecommendations)

class Friends(Document):
    user_id = StringField(default='')
    friends = ListField(default=[])
    meta = {
        'indexes': ['user_id']
    }




        
