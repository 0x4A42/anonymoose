class Config:
    """
    This class will represent values that will will want to be saved so that the bot does not need to
    be configured every time it starts up.
    An object of this class will be saved to file and read in upon bot start.

    Args/Variables:
        initial_channel(int): The ID of the channel you want messages copied from
        moved_channel(int): The ID of the channel you want messages copied to
        prefix(string): The prefix for interacting wit the bot, defaults to '$'.
    """
    def __init__(self, prefix, initial_channel, moved_channel):
        self.__initial_channel = initial_channel
        self.__moved_channel = moved_channel
        self.__prefix = prefix
        self.allowed_prefixes = ["!", "£", "$", "%", "^", "&", "*", "."]

    def print_values(self):
        print(self.__prefix)
        print(self.__initial_channel)
        print(self.__moved_channel)

    @property
    def prefix(self):
        return self.__prefix

    @prefix.setter
    def prefix(self, new_prefix):
        if new_prefix in self.allowed_prefixes:
            self.__prefix = new_prefix
        else:
            pass

    @property
    def initial_channel(self):
        return self.__initial_channel

    @initial_channel.setter
    def initial_channel(self, new_initial_channel):
        self.__initial_channel = new_initial_channel

    @property
    def moved_channel(self):
        return self.__moved_channel

    @moved_channel.setter
    def moved_channel(self, new_moved_channel):
        self.__moved_channel = new_moved_channel

