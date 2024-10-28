from app.models.user import User
from app.repositories.i_repository import IRepository

class UserRepository(IRepository):
    
    def get_all(self):
        return User.objects.all()

    def show_all(self):
        users = User.objects.all()
        for user in users:
            print(user)
            print()
        print()
    
    def get_by_id(self, u_id):
        try:
            return User.objects.get(id = u_id)
        except User.DoesNotExist:
            print(f"Error: User with id: {u_id} does not exist.")
            return None

    def __is_email_unique(self, email):
        if User.objects.filter(email=email).exists():
            print(f"Error: User with email '{email}' already exists.")
            return False
        return True

    def __is_phone_number_unique(self, phone_number):
        if User.objects.filter(phone_number=phone_number).exists():
            print(f"Error: User with phone number '{phone_number}' already exists.")
            return False
        return True

    def __is_password_unique(self, password):
        if User.objects.filter(password=password).exists():
            print(f"Error: User with this password already exists. Please choose a different password.")
            return False
        return True

    def create(self, first_name, last_name, phone_number, email, password):
        if (not self.__is_email_unique(email)):
            return None
        if (not self.__is_phone_number_unique(phone_number)):
            return None
        if (not self.__is_password_unique(password)):
            return None
        user = User(
            first_name = first_name, 
            last_name = last_name,
            phone_number = phone_number,
            email = email,
            password = password
        )
        user.save()
        return user

    def update(self, user, first_name=None, last_name=None, phone_number=None, email=None, password=None):
        if (first_name is not None):
            user.first_name = first_name
        if (last_name is not None):
            user.last_name = last_name
        if (phone_number is not None):
            user.phone_number = phone_number
        if (email is not None):
            user.email = email
        if (password is not None):
            user.password = password  
        
        user.save()
        return user