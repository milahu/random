
import sys, importlib

def import_from_string(name: str, source: str):
  "Import module from source string"
  spec = importlib.util.spec_from_loader(name, loader=None)
  module = importlib.util.module_from_spec(spec)
  exec(source, module.__dict__)
  sys.modules[name] = module

import_from_string('hello_module', '''
  def hello():
    print('hello')
''')

hello_module.hello()
