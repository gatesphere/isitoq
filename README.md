isitoq
======

A pure boolean logic/stack language focused on testing, with built in 
assertions

Overview
--------
From [Wikipedia](http://en.wikipedia.org/wiki/Issitoq):

    In Inuit mythology, Issitoq (also Isitoq) is a deity that punishes 
    those who break taboos. He usually takes the form of a giant flying 
    eye.
    
Isitoq is a programming language centered around the idea of testing.  
It is extremely minimal, consisting of a single datatype (boolean values),
and a few operations which revolve around comparing values.  It has a 
single universal operation, `?` (the test operation) which is universal 
and functionally complete, as it can implement a simple NOR gate.

Isitoq will berate users for breaking programs, or for writing assertions
that fail.  However, it won't necessarily be easy to figure out what
you did wrong.

This language is an entry in the 
[January 2013 PLTGames competition](http://www.pltgames.com/competition/2013/1).

License
-------
Isitoq is [BSD Licensed](https://raw.github.com/gatesphere/isitoq/master/license/license.txt).

How Isitoq Works
----------------
Isitoq programs work on a single main stack, with new stacks defined
on the fly for each function call, to prevent value leakage.

When calling a function, it pops the correct number of arguments off of
the stack, pushes them in the correct order onto a new stack, and then
operates on that new stack.  After function execution, the function 
stack is destroyed.

Aside from function calls, there are two literal value words that simply
push values to the stack, `t` and `f`, which represent true and false, 
respectively.

There are also two operators which work similarly.  The main operator
is the `?` (test) operator, which needs at least one comparison value
to check the value(s) at the top of the stack against.  If they match, 
a `t` is pushed to the stack, else a `f` is pushed to the stack.

The last operator is the `!` (assert) operator.  `!` operates similarly 
to `?`, except that it does not push a value to the stack.  Instead, it 
will halt your program and make Ishitoq angry if it's values do not match
the top of the stack.  Otherwise, the program continues along silently.

Both `?` and `!` check the values on top of their current stack (function
or main), but `?` pushes it's results to the parent stack.  This is how
values are returned from functions.

As you may have gleaned, the only way to pop values from the stack is by
calling a function, and the main way of getting anything accomplished is
by using the `?` operator.  This system is functionally complete by virtue
of the fact that NOR can be defined like so:

    // define the `nor` function
    :nor .. -> ?f|f
    // :nor = define a function named nor
    // ..   = that takes two parameters
    // ->   = and has a body that specifies...
    // ?f|f = if the top two values of the current stack 
    //        (the function stack) are `f`, push a `t` to
    //        the calling stack

From this, we can define all of the other logic gates:

    :id .    -> ?t ?t // duplicate the top item on the calling stack
    :not .   -> id nor ?t
    :and ..  -> ?t|t
    :nand .. -> and not ?t
    :or ..   -> nor not ?t
    :xor ..  -> or . .. nand and ?t
    :xnor .. -> xor not ?t

I wouldn't call Isitoq Turing complete, but you can accomplish a lot 
with these fundamental building blocks.

Getting Isitoq
--------------
Getting Isitoq is dead simple:

  1. Get Python 2.7 (not Python 3+)
  2. Clone this repo
  
You've got a working Isitoq distribution now.

Using Isitoq
------------
Isitoq may be invoked like so:

    python isitoq.py
    
But this will give you errors:

    $ python isitoq.py
    usage: python isitoq.py [-d] <filename.isq>
           python isitoq.py -v
           python isitoq.py -h
      -d: display debug information
      -v: display version info and exit
      -h: display this help text and exit

I'm sure you can figure it out from here.

Isitoq's Grammar
----------------
Here's the grammar, in modified EBNF:

    program     := {line}
    line        := fn_defn | cmd_line
    fn_defn     := name, argspec, "->", fn_cmd_line
    name        := {[A-Za-z0-9]}+
    argspec     := {"."}+
    cmd_line    := {word}+
    fn_cmd_line := {fn_word}+
    word        := name | value | test | assert
    fn_word     := word | argspec
    value       := "t" | "f"
    test        := "?", value, {"|", value}
    assert      := "!", value, {"|", value}
    
Comments are delineated by `//` to the end of the line.

Example Program
---------------
    // define some functions
    :id . -> ?t ?t
    :nor .. -> ?f|f
    :not .   -> id nor ?t
    :and ..  -> ?t|t
    :nand .. -> and not ?t
    :or ..   -> nor not ?t
    :xor ..  -> or . .. nand and ?t
    :xnor .. -> xor not ?t

    // do some things
    t id !t|t   // push t to the stack, duplicate, and assert that top of stack is [t, t]<=
    id !t|t|t   // duplicate top of stack, assert that top of stack is [t, t, t]<=
    nor !f      // nor the top two items, and assert that top of stack is f
    nor !f      // same
    id nor !t   // dup, nor, assert t
    not !f      // negate, assert f
    t nand !t   // push t, nand, assert t
    f !f|t      // push f, assert top of stack is [t, f]<=
    ?t|f !f|f|t // test if top of stack is [f, t]<=, assert [t, f, f]<=
    
The output of this program is as follows:

    $ python isitoq.py test.isq
    ISITOQ has contemplated your input, and determined the following:
    [t, f, f]<==
    BE HAPPY, MORTAL, THAT YOUR PROGRAM RAN WITHOUT FLAWS.
    
With debugging, it's like this:

    $ python isitoq.py -d test.isq
    STACK BEFORE WORD t: []<==
    STACK BEFORE WORD id: [t]<==
      STACK BEFORE WORD ?t: [t]<==
      STACK BEFORE WORD ?t: [t]<==
    STACK BEFORE WORD !t|t: [t, t]<==
    STACK BEFORE WORD id: [t, t]<==
      STACK BEFORE WORD ?t: [t]<==
      STACK BEFORE WORD ?t: [t]<==
    STACK BEFORE WORD !t|t|t: [t, t, t]<==
    STACK BEFORE WORD nor: [t, t, t]<==
      STACK BEFORE WORD ?f|f: [t, t]<==
    STACK BEFORE WORD !f: [t, f]<==
    STACK BEFORE WORD nor: [t, f]<==
      STACK BEFORE WORD ?f|f: [t, f]<==
    STACK BEFORE WORD !f: [f]<==
    STACK BEFORE WORD id: [f]<==
      STACK BEFORE WORD ?t: [f]<==
      STACK BEFORE WORD ?t: [f]<==
    STACK BEFORE WORD nor: [f, f]<==
      STACK BEFORE WORD ?f|f: [f, f]<==
    STACK BEFORE WORD !t: [t]<==
    STACK BEFORE WORD not: [t]<==
      STACK BEFORE WORD id: [t]<==
        STACK BEFORE WORD ?t: [t]<==
        STACK BEFORE WORD ?t: [t]<==
      STACK BEFORE WORD nor: [t, t]<==
        STACK BEFORE WORD ?f|f: [t, t]<==
      STACK BEFORE WORD ?t: [f]<==
    STACK BEFORE WORD !f: [f]<==
    STACK BEFORE WORD t: [f]<==
    STACK BEFORE WORD nand: [f, t]<==
      STACK BEFORE WORD and: [f, t]<==
        STACK BEFORE WORD ?t|t: [f, t]<==
      STACK BEFORE WORD not: [f]<==
        STACK BEFORE WORD id: [f]<==
          STACK BEFORE WORD ?t: [f]<==
          STACK BEFORE WORD ?t: [f]<==
        STACK BEFORE WORD nor: [f, f]<==
          STACK BEFORE WORD ?f|f: [f, f]<==
        STACK BEFORE WORD ?t: [t]<==
      STACK BEFORE WORD ?t: [t]<==
    STACK BEFORE WORD !t: [t]<==
    STACK BEFORE WORD f: [t]<==
    STACK BEFORE WORD !f|t: [t, f]<==
    STACK BEFORE WORD ?t|f: [t, f]<==
    STACK BEFORE WORD !f|f|t: [t, f, f]<==
    ISITOQ has contemplated your input, and determined the following:
    [t, f, f]<==
    BE HAPPY, MORTAL, THAT YOUR PROGRAM RAN WITHOUT FLAWS.

Happy Hacking!
