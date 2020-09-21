

class Config:
    """
    Initiates the class, setting up the environment

    Args/Variables:
        initial_channel(int): The ID of the channel you want messages copied from
        moved_channel(int): The ID of the channel you want messages copied to
        prefix(string): The prefix for interacting wit the bot, defaults to '$'.
    """
    def __init__(self, initial_channel, moved_channel, prefix="$"):
        self.prefix = prefix
        self.initial_channel = initial_channel
        self.moved_channel = moved_channel

    def print_values(self):
        print(self.prefix)
        print(self.initial_channel)
        print(self.moved_channel)



