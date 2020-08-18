#!/usr/bin/python3

import sys
from lark import Lark
from lark import Transformer

# Common grammars can be found here:
# https://github.com/lark-parser/lark/blob/master/lark/grammars/common.lark

default_string = "Ala has 2 cats. She is a #catlover."

parser = Lark(r"""

    doc: phrase+

    phrase: (literal | hashtag)+ "."
    literal: WORD | DIGIT+
    hashtag: "#" literal

    %import common.DIGIT
    %import common.WORD
    %import common.WS
    %ignore WS

    """, start='doc')

class TextToListTransformer(Transformer):

    def literal(self, s):
        s, = s
        if s.type == 'DIGIT':
            return int(s)
        return ("%s" % s)

    def hashtag(self, s):
        s, = s
        return("#" + s.upper())

    doc = list
    phrase = list

ast = parser.parse(" ".join(sys.argv[1:] or [default_string]))
asl = TextToListTransformer().transform(ast)

for p in (ast.pretty(), ast, asl):
    print ("%s\n\n" % p)


