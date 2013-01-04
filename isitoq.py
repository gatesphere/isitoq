# isitoq
# PeckJ 20130104
#

import sys, getopt


######################
## globals
isitoq_version = "20130104"
isitoq_funtion_lookup_table = {}
isitoq_debug = False


isitoq_main_stack = [];
isitoq_calling_stack = [isitoq_main_stack];

######################
## interpreter
class IsitoqException(Exception):
  def __init__(self, msg):
    self.msg = msg

def interpret_file(file):
  with open(file) as f:
    lines = f.readlines()
  
  for line in lines:
    try:
      interpret_line(line);
    except IsitoqException as e:
      raise

def interpret_line(line):
  if len(line.strip()) == 0:
    return
  if is_fn_defn(line): 
    try:
      interpret_fn_defn(line)
    except IsitoqException as e:
      raise
  elif is_cmd(line): 
    try:
      interpret_cmd(line)
    except IsitoqException as e:
      raise
  else:
    raise IsitoqException("The line -- %s -- HAS ANGERED ISITOQ" 
                          % line.strip())

def is_fn_defn(line):
  line = line.strip()
  if line.startswith(":"):
    line = line[1:]
    tokens = line.split()
    return (len(tokens) > 4 and 
            is_valid_name(tokens[0]) and 
            is_valid_argspec(tokens[1]) and
            tokens[2] == "->")
  return False

def is_valid_name(name):
  # fn names may only be alphanumeric
  return name.isalnum()

def is_valid_argspec(argspec):
  # argspec must consist of 1+ . characters only
  return len(argspec) > 0 and argspec.count(".") == len(argspec)

def is_valid_operator(op):
  return op.startswith("?") or op.startswith("!")

def is_comment(comment):
  return comment.startswith("//")

def is_cmd(line):
  # if it's not a fn defn, it's a command by definition...
  # unless it contains illegal characters, that is
  for token in line.split():
    if not (is_valid_name(token) or is_valid_operator(token)):
      if is_comment(token):
        return True # break on comments - rest of line is garbage
      return False
  return True

def interpret_fn_defn(fn):
  global isitoq_debug
  if isitoq_debug:
    print "FN defn: %s" % fn.strip()
  pass
  
def interpret_cmd(cmd):
  global isitoq_debug
  if isitoq_debug:
    print "cmd line: %s" % cmd.strip()
  for word in cmd.partition("//")[0].split():
    try:
      interpret_word(word)
    except IsitoqException as e:
      raise

def interpret_word(word):
  global isitoq_calling_stack, isitoq_main_stack
  if is_value(word):
    isitoq_calling_stack[-1].append(value(word))
  elif is_test(word):
    pass # stub
  elif is_assert(word):
    pass # stub
  elif is_fn_call(word):
    pass # stub
  else:
    raise IsitoqException("Isitoq does not know of the word -- %s -- and is VERY ANGRY" % word)

def is_value(val):
  return val == "t" or val == "f"
  
def value(val):
  return val == "t"

def is_test(test):
  return test.startswith("?")

def is_assert(a):
  return a.startswith("!")

def is_fn_call(fn):
  if isitoq_funtion_lookup_table.get(fn, None): return True
  else: return False

######################
## front end
def usage():
  print "usage: python isitoq.py [-d] <filename.isq>"
  print "       python isitoq.py -v"
  print "       python isitoq.py -h"
  print "  -d: display debug information"
  print "  -v: display version info and exit"
  print "  -h: display this help text and exit"
  
def version():
  global isitoq_version
  print "isitoq version %s" % isitoq_version
  print "Jacob Peck (suspended-chord)"
  print "http://github.com/gatesphere/isitoq"
  
if __name__ == "__main__":
  args = sys.argv[1:]
  try:
    opts, args = getopt.getopt(args, 'dvh')
  except:
    usage()
    sys.exit()
  pversion, phelp = False, False
  for opt, a in opts:
    if   opt == '-v': pversion = True
    elif opt == '-h': phelp = True
    elif opt == '-d': isitoq_debug = True
  if pversion:
    version()
    sys.exit()
  if len(args) != 1 or phelp:
    usage()
    sys.exit()
  
  filename = args[0]

  ## actual logic
  try:
    interpret_file(filename)
  except IsitoqException as e:
    print "Isitoq judges your program FLAWED: "
    print e.msg
    if isitoq_debug:
      print "main stack contents"
      print isitoq_main_stack
    sys.exit()
  
  sys.exit()
