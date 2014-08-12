from lbm_mong.models import Person

def test(backend, user, response, *args, **kwargs):
    email = kwargs['details']['email']
    uid = kwargs['uid']
    Person.objects(email=email).update(set__uid=uid)

