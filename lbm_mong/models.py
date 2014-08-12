from datetime import datetime
from mongoengine.django.auth import User
from mongoengine import *
from mongoengine import signals
from signals import send_push, generate_random_token, send_email     

class Message(Document):
    username = StringField(max_length=20, required=True)
    recipient = StringField(max_length=20, required=True)
    message = StringField(required=True)
    date_sent = DateTimeField(default=datetime.now)
    received = BooleanField(default=False)

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        return super(Message, self).save(*args, **kwargs)

signals.post_save.connect(send_push, sender=Message)

'''Extends mongoengine.django.auth User model to include API token field'''
class Person(User):
    api_token = StringField(default='')
    access_token = StringField(default='') #new
    email = EmailField(unique=True)
    uid = StringField(default='')

signals.pre_save.connect(generate_random_token, sender=Person)                             



class EmailRecommendations(Document):
    email = EmailField(required=True)
    username = StringField(max_length=20, required=True)

    def __unicode__(self):
        return self.username

    def save(self, *args, **kwargs):
        return super(EmailRecommendations, self).save(*args, **kwargs)

signals.post_save.connect(send_email, sender=EmailRecommendations)

class Friends(Document):
    uid = StringField(default='')
    friends = ListField(default=[])
    user_id = StringField(default='')




        
