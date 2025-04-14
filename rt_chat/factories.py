from abc import abstractmethod

class GroupCreator:
    @abstractmethod
    def factory_method(self):
        pass

    def createGroup(self):
        # Call the factory method to create a Product object.
        group = self.factory_method()

        return group
    
# class PrivateGroupCreator:
    