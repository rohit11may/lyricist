import pickle


def save(obj, filename, verbose=False):
    with open(filename, 'wb') as f:
        pickle.dump(obj, f)
    if verbose: print("Saved at {}!".format(filename))


def load(filename, verbose=False):
    with open(filename, 'rb') as f:
        obj = pickle.load(f)
    if verbose: print("Loaded from {}!".format(filename))
    return obj
