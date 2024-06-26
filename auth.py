from database import get_user_by_phone

def authorize_user(phone_number):
    user = get_user_by_phone(phone_number)
    
    if user:
        user_data = {
            'id': user[0],
            'store_id': user[1],
            'role': user[3],
            'name': user[4]
        }
        return user_data
    else:
        return None
