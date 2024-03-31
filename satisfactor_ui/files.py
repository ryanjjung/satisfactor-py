import pickle

from satisfactor_py.factories import Factory

def save_factory(
    factory: Factory,
    filename: str
):
    '''
    Pickles the given factory and saves that content to the specified file
    '''

    with open(filename, 'wb') as fh:
        pickle.dump(factory, fh, pickle.HIGHEST_PROTOCOL)

def load_factory(
    filename: str
) -> Factory:
    with open(filename, 'rb') as fh:
        factory = pickle.load(fh)
    
    return factory