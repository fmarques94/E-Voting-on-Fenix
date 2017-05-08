def save_profile(backend, user, response, *args, **kwargs):
    if backend.name == 'fenix':
        user.name = response.get('name')
        user.email = response.get('email')
        user.save()

def printSomething(backend, user, response, *args, **kwargs):
    print(user)
    print(backend)
    print(args)
    print(kwargs)