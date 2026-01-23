from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q


class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend that allows users to authenticate using their email address.
    Email comparison is case-insensitive.
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate a user using their email address (case-insensitive).
        
        Args:
            request: HttpRequest object
            username: Email address provided by the user
            password: Password provided by the user
            **kwargs: Additional keyword arguments
            
        Returns:
            User object if authentication is successful, None otherwise
        """
        UserModel = get_user_model()
        
        if username is None or password is None:
            return None
        
        try:
            # Find user by email (case-insensitive)
            user = UserModel.objects.get(
                Q(email__iexact=username) | Q(email__iexact=username.lower())
            )
        except UserModel.DoesNotExist:
            # Run the default password hasher once to reduce timing difference
            # between existing and non-existing users
            UserModel().set_password(password)
            return None
        except UserModel.MultipleObjectsReturned:
            # Handle edge case where multiple users have same email (shouldn't happen with unique constraint)
            return None
        
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        return None
    
    def get_user(self, user_id):
        """
        Retrieve a user by their ID.
        
        Args:
            user_id: Primary key of the user
            
        Returns:
            User object if found, None otherwise
        """
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None