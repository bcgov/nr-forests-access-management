import pytest
from api.app.utils.utils import mask_string


def test_mask_string_short():
    assert mask_string('abc', 5) == 'abc'

def test_mask_string_exact():
    assert mask_string('hello', 5) == 'hello'

def test_mask_string_masked():
    assert mask_string('abcdef', 2) == 'ab****'

def test_mask_string_partial():
    assert mask_string('abcdef', 4) == 'abcd**'

def test_mask_string_empty():
    assert mask_string('', 3) == ''
