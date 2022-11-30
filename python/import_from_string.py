import sys, importlib.util

def import_from_string(name: str, source: str):
  """
  Import module from source string.
  Example use:
  import_from_string("m", "f = lambda: print('hello')")
  m.f()
  """
  spec = importlib.util.spec_from_loader(name, loader=None)
  module = importlib.util.module_from_spec(spec)
  exec(source, module.__dict__)
  sys.modules[name] = module
  globals()[name] = module

# demo

# note: "if True:" allows to indent the source string
import_from_string('hello_module', '''if True:
  def hello():
    print('hello')
''')

hello_module.hello()
