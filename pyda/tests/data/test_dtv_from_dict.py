import numpy as np
import pyds_model

from pyda.data._data import anydata_from_dict


def test_anydata_from_dict__empty():
    result = anydata_from_dict({})
    assert isinstance(result, pyds_model._ds_model.AnyData)


def test_anydata_from_dict__unusual_key():
    result = anydata_from_dict({'Are we allowed special chars?! 🙈': 1})
    assert 'Are we allowed special chars?! 🙈' in result


def test_anydata_from_dict__int():
    result = anydata_from_dict({'a': 1})
    # Type casting is platform specific (np.int_)
    assert isinstance(result['a'], np.int_)


def test_anydata_from_dict__float():
    result = anydata_from_dict({'a': 1.23})
    # Type casting is platform specific (np.float_)
    assert isinstance(result['a'], np.float_)


def test_anydata_from_dict__float32():
    result = anydata_from_dict({'a': np.float32(1.2)})
    assert isinstance(result['a'], np.float32)


def test_anydata_from_dict__array_int8():
    result = anydata_from_dict({'a': np.arange(2, 7).astype(np.int8)})
    assert result['a'].dtype == np.int8
    np.testing.assert_array_equal(result['a'], [2, 3, 4, 5, 6])


def test_anydata_from_dict__str():
    result = anydata_from_dict({'a': 'hello world'})
    assert isinstance(result['a'], str)


def test_anydata_from_dict__list_double():
    result = anydata_from_dict({'a': [1, 1.2, -5]})
    assert isinstance(result['a'], np.ndarray)
    assert result['a'].dtype == np.float_
    np.testing.assert_array_equal(result['a'], [1, 1.2, -5])


def test_anydata_from_dict__list_poly():
    result = anydata_from_dict({'a': [1, 1.2, 'a string']})
    assert isinstance(result['a'], np.ndarray)
    np.testing.assert_array_equal(result['a'], ['1', '1.2', 'a string'])
