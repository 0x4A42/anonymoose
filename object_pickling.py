import pickle

"""
This script contains functions relating to the saving and loading of pickle files,
which contain the Config object. 
"""


def save_pickle(config_file_name, config):
    """
    Saves the current version of the CONFIG object to a pickle file so that it can be reused.]

    Args:
        config_file_name: the name of the pickle file
        config: the global CONFIG object
    """
    pickle.dump(config, open(config_file_name, "wb"))


def load_pickle(config_file_name):
    """
    Loads the pickle file in, which contains the CONFIG object.
    """
    with open(config_file_name, 'rb') as pickle_file:
        CONFIG = pickle.load(pickle_file)
        return CONFIG
