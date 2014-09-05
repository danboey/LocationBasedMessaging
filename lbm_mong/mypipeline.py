from lbm_mong.models import MyUser

'''Custom pipeline to add email and facebook uid to user model during registration/facebook auth process'''
def my_pipeline(backend, user, response, *args, **kwargs):
    email = kwargs['details']['email']
    uid = kwargs['uid']
    MyUser.objects(email=email).update(set__user_id=uid)

