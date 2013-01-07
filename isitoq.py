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
isitoq_bindings = [];
isitoq_calling_stack = [isitoq_main_stack];

######################
## interpreter
class IsitoqException(Exception):
  def __init__(self, msg):
    self.msg = msg

class IsitoqFunction:
  def __init__(self, name, argcount, body):
    self.name = name
    self.argcount = argcount
    self.body = body

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
    return (len(tokens) > 3 and 
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
  global isitoq_debug, isitoq_funtion_lookup_table
  fn = fn[1:].split()
  name, argcount, body = fn[0], len(fn[1]), fn[3:]
  if isitoq_funtion_lookup_table.get(name, None): 
    raise IsitoqException("Multiple definitions of -- %s -- make ISITOQ ANGRY" % name)
  else:
    isitoq_funtion_lookup_table[name] = IsitoqFunction(name, argcount, body)
  pass
  
def interpret_cmd(cmd):
  global isitoq_debug
  for word in cmd.partition("//")[0].split():
    try:
      interpret_word(word)
    except IsitoqException as e:
      raise

def interpret_word(word):
  global isitoq_calling_stack, isitoq_main_stack, isitoq_debug, isitoq_bindings
  current_stack = isitoq_calling_stack[-1]
  in_fn_call = len(isitoq_calling_stack) > 1
  if in_fn_call:
    prev_stack = isitoq_calling_stack[-2]
    bindings = isitoq_bindings[-1]
  if isitoq_debug:
    print "%sSTACK BEFORE WORD %s: %s" % ("  "*(len(isitoq_calling_stack)-1), 
                                          word, print_stack(current_stack))
  ## push a value
  if is_value(word):
    current_stack.append(value(word))
    
  ## run a test
  elif is_test(word):
    test = map(value, list(word[1:].split("|")))
    try:
      vals = current_stack[-len(test):]
      vals.reverse()
    except:
      raise IsitoqException("ISITOQ can't make truth from nothing!")
    if test[:] == vals[:]:
      if in_fn_call:
        prev_stack.append(True)
      else:
        current_stack.append(True)
    else:
      if in_fn_call:
        prev_stack.append(False)
      else:
        current_stack.append(False)
  
  ## run an assertion
  elif is_assert(word):
    atest = map(value, list(word[1:].split("|")))
    try:
      vals = current_stack[-len(atest):]
      vals.reverse()
    except:
      raise IsitoqException("ISITOQ can't make truth from nothing!")
    if atest[:] != vals[:]:
      raise IsitoqException("YOUR ASSERTION -- %s -- FAILED, MORTAL." % word)
  
  ## call a fn
  elif is_fn_call(word):
    # grab fn defn
    fn = isitoq_funtion_lookup_table[word]
    # create new stack
    newstack = []
    # pop args from original stack
    args = []
    try:
      for i in range(fn.argcount):
        args.append(current_stack.pop())
    except:
      raise IsitoqException("ISITOQ can't make truth from nothing!")
    # push onto new stack in proper order
    for arg in reversed(args):
      newstack.append(arg)
    # create bindings
    isitoq_bindings.append(args)
    # add new stack to the calling stack
    isitoq_calling_stack.append(newstack)
    # interpret words
    for w in fn.body:
      interpret_word(w)
    # delete stack
    isitoq_calling_stack.pop()
  
  ## bindings while in functions
  elif in_fn_call and is_binding(word):
    arg = len(word)
    if arg > len(bindings):
      raise IsitoqException("ISITOQ cannot decipher the word -- %s -- and is NOT TO BE TRIFLED WITH, MORTAL" % word)
    else:
      current_stack.append(bindings[arg - 1])
  
  ## not a valid word
  else:
    raise IsitoqException("ISITOQ does not know of the word -- %s -- and is VERY ANGRY" % word)

def is_value(val):
  return val == "t" or val == "f"
  
def value(val):
  return val == "t"

def is_test(test):
  if test.startswith("?"):
    for x in test[1:].split("|"):
      if not is_value(x): 
        return False
    return True
  else:
    return False

def is_assert(a):
  return a.startswith("!")

def is_fn_call(fn):
  if isitoq_funtion_lookup_table.get(fn, None): return True
  else: return False
  
def is_binding(bind):
  return is_valid_argspec(bind)

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
  
def print_stack(stack):
  # magic:
  # "ft"[True] == "t", "ft"[False] == "f"
  return "[%s]<==" % ", ".join(map(lambda x: "ft"[x], stack))

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
    print "ISITOQ judges your program FLAWED for committing the following sin: "
    print e.msg
    if isitoq_debug:
      print "  main stack contents"
      print "  %s" % print_stack(isitoq_main_stack)
      print "  function definitions"
      print "  %s" % isitoq_funtion_lookup_table
    else:
      print "ISITOQ has no MERCY for fools who don't DEBUG."
    sys.exit()
  print "ISITOQ has contemplated your input, and determined the following:"
  print print_stack(isitoq_main_stack)
  print "BE HAPPY, MORTAL, THAT YOUR PROGRAM RAN WITHOUT FLAWS."
  sys.exit()
