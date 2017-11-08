grammar m;

expression: op_add ((GT|LT|GE|LE) op_add)*;

op_add: op_mul ((ADD|SUB) op_mul)*;

op_mul: atom (MUL atom)*;

dummy_unary_add: (ADD|SUB)*;

atom: (
        (p=dummy_unary_add i=INT)
        |(p=dummy_unary_add f=FLOAT)
        |(p=dummy_unary_add m=M)
        |(p=dummy_unary_add '(' e=expression ')')
        |(p=dummy_unary_add c=(INT|FLOAT) m2=M)
      );

start_rule: expression;

INT: ('0' .. '9')+;

FLOAT: INT '.' (INT| INT ('E'|'e') SUB? INT);

GT: '>';

GE: '>=';

LT: '<';

LE: '<=';

M: 'm';

ADD: '+';

SUB: '-';

MUL: '*';

WS: (' '|'\n'|'\r'|'\t') -> skip;