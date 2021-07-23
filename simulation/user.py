# User class
# Attributes: id, 
# is_busy (to indicate is the user already assigned to some trip)
class User:
    def __init__(self, id: str):
        self.id = id
        self.is_busy = False


    def get_user_id(self):
        return self.user_id

    def get_is_busy(self):
        return self.is_busy

    def set_user_id(self,user_id):
        self.id = user_id

    def free_user(self):
        self.is_busy = False

    def change_status_to_busy(self):
        self.is_busy = True
    