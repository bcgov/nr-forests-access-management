import unittest
import importlib
import logging
import jsonpickle
import json


logger = logging.getLogger()

function = __import__('lambda_function')
handler = function.lambda_handler

def execute_function(filename):
  file = open(filename)
  try:
    event = jsonpickle.decode(file.read())
    context = {'requestid' : '1234'}
    result = handler(event, context)
  finally:
    file.close()
  file.close()  
  return result

class TestFunction(unittest.TestCase):

  def test_dogs_success(self):
    result = execute_function('event.json')
    self.assertRegex(str(result), 'dogs', 'Should match')
    self.assertNotRegex(str(result), 'cats', 'Should not match')

  def test_cats_success(self):
    result = execute_function('event2.json')
    self.assertRegex(str(result), 'cats', 'Should match') 
    self.assertNotRegex(str(result), 'dogs', 'Should not match')

if __name__ == '__main__':
    unittest.main()


