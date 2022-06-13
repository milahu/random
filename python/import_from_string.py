# import module from source string
# https://stackoverflow.com/questions/5362771/how-to-load-a-module-from-code-in-a-string

# `imp.new_module` is deprecated [1] since python 3.4,
# but it still works as of python 3.9
# 
# `imp.new_module` was replaced with `importlib.util.module_from_spec`
# 
# > importlib.util.module_from_spec [2]
# > is preferred over using `types.ModuleType` to create a new module as
# > spec is used to set as many import-controlled **attributes on the module**
# > as possible.
# > 
# > importlib.util.spec_from_loader [3]
# > uses available loader APIs, such as `InspectLoader.is_package()`, to
# > fill in any missing information on the spec.
# 
# these module attributes are `__builtins__` `__doc__` `__loader__` `__name__` `__package__` `__spec__`
# 
# [1] https://docs.python.org/3/library/imp.html#imp.new_module
# [2] https://docs.python.org/3/library/importlib.html#importlib.util.module_from_spec
# [3] https://docs.python.org/3/library/importlib.html#importlib.util.spec_from_loader


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
