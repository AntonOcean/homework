from unittest import TestCase
from tempfile import TemporaryDirectory
from dir_dict import DirDict


class DictTestCase(TestCase):
    def setUp(self):
        self.temp_dir = TemporaryDirectory()
        self.dict = DirDict(self.temp_dir.name)
        self.dict['test'] = 'My test\n'
        self.dict['lang'] = 'Python\n'
        self.dict['place'] = ['String\n', 'This is']

    def test_get(self):
        my_dict = self.dict
        key = my_dict.get('place')
        self.assertEqual(key, str(['String\n', 'This is']))
        key = my_dict.get('kk')
        self.assertEqual(key, None)

    def test_items(self):
        my_dict = self.dict
        self.assertEqual(len(my_dict), 3)
        self.assertEqual(len(my_dict), len(my_dict.items()))

    def test_values(self):
        my_dict = self.dict
        value = next(iter(my_dict.values()))
        self.assertTrue(value)

    def test_keys(self):
        my_dict = self.dict
        key = next(iter(my_dict.keys()))
        value = my_dict.get(key)
        self.assertTrue(value in my_dict.values())

    def test_pop(self):
        my_dict = self.dict
        self.assertEqual(len(my_dict), 3)
        elem = my_dict.pop('lang')
        self.assertEqual(elem, 'Python\n')
        self.assertEqual(len(my_dict), 2)

    def test_popitem(self):
        my_dict = self.dict
        self.assertEqual(len(my_dict), 3)
        my_dict.popitem()
        self.assertEqual(len(my_dict), 2)

    def test_update(self):
        my_dict = self.dict
        self.assertEqual(len(my_dict), 3)
        my_dict.update({'bmstu': 7864})
        self.assertEqual(len(my_dict), 4)
        self.assertEqual(my_dict.get('bmstu'), '7864')

    def test_clear(self):
        my_dict = self.dict
        self.assertTrue(my_dict)
        my_dict.clear()
        self.assertEqual(my_dict, {})
