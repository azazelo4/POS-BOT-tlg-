from database import get_user_by_phone

def authorize_user(phone_number):
    user = get_user_by_phone(phone_number)
    
    if user:
        return user
    else:
        return None
