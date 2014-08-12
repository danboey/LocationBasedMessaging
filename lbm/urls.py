from django.conf.urls import patterns, include, url
from django.conf import settings
from tastypie.api import Api
from django.conf.urls import *
from lbm_mong.api import MessageResource, SocialSignUpResource, EmailRecommendationResource, SentMessageResource, ReceivedMessageResource, PullMessageResource, FriendsResource

message_resource = MessageResource()
social_resource = SocialSignUpResource()
email_resource = EmailRecommendationResource()
sent_resource = SentMessageResource()
received_resource = ReceivedMessageResource() 
pull_resource = PullMessageResource() 
friends_resource = FriendsResource()

urlpatterns = patterns('',
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^api/', include(social_resource.urls)),
    url(r'^api/', include(message_resource.urls)),
    url(r'^api/', include(email_resource.urls)),
    url(r'^api/', include(sent_resource.urls)),
    url(r'^api/', include(received_resource.urls)),
    url(r'^api/', include(pull_resource.urls)),
    url(r'^api/', include(friends_resource.urls)),
)
