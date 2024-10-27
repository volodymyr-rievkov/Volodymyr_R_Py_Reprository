from app.models import User
from app.repositories.i_repository import IRepository

class UserRepository(IRepository):
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

    def create(self, u_first_name, u_last_name, u_phone_number, u_email, u_password):
        if (not self.__is_email_unique(u_email)):
            return None
        if (not self.__is_phone_number_unique(u_phone_number)):
            return None
        if (not self.__is_password_unique(u_password)):
            return None
        user = User(
            first_name = u_first_name, 
            last_name = u_last_name,
            phone_number = u_phone_number,
            email = u_email,
            password = u_password
        )
        user.save()
        return user

    