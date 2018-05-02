from collections.abc import MutableMapping
import os
import glob


class DirDict(MutableMapping):
    def __init__(self, path):
        self.path = path
        if os.path.exists(path):
            self.clear()
        else:
            os.makedirs(path)
        self._dict = os.listdir(self.path)
        super(DirDict, self).__init__()

    @property
    def dict(self):
        return os.listdir(self.path)

    def __getitem__(self, item):
        try:
            with open(os.path.join(self.path, item), 'r') as file:
                return file.read()
        except FileNotFoundError:
            raise KeyError

    def __setitem__(self, key, value):
        with open(os.path.join(self.path, key), 'w') as file:
            file.write(str(value))

    def __iter__(self):
        for element in self.dict:
            yield element

    def __len__(self):
        return len(self.dict)

    def __delitem__(self, key):
        file = glob.glob(os.path.join(self.path, key))[0]
        os.remove(file)

    def __repr__(self):
        view_dict = {}
        for element in self.dict:
            with open(os.path.join(self.path, element)) as file:
                view_dict[element] = file.read()
        return str(view_dict)
