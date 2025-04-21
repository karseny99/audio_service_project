from dataclasses import dataclass
from datetime import datetime
from .value_objects.email import EmailAddress
from .value_objects.password_hash import PasswordHash
from .value_objects.username import Username

@dataclass(frozen=False)  
class User:
    id: int
    email: EmailAddress          
    username: Username           
    password_hash: PasswordHash  
    created_at: datetime = datetime.utcnow()  
    
    def change_password(self, new_password_hash: PasswordHash) -> None:
        """
            Updates user's password
        """
        self.password_hash = new_password_hash


