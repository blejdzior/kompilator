grammar asd;
prog:  expr*  EOF ;
expr: value ADD value #add
    | var '=' arrAss #arrayAssign
    | var '=' (value | expr) #assign
    | ID ('[' INT ']') '=' (value | expr) #elementAssign
    | PRINT '(' value ')' #print
    | READ '(' ID ')' #read
    | value MULT value #mult
    | value DIV value #div
    | value SUB value #sub
    | booleanOperation # booleanOp
    ;
booleanOperation: andOp # and
                | orOp # or
                | xorOp # xor
                | negOp # neg
                ;
arrAss: '[' value (',' value)* ']' # array;
andOp: value AND (value | booleanOperation);
orOp : value OR (value | booleanOperation);
xorOp: value XOR (value |  booleanOperation);
negOp: NEG  value
     | NEG '(' booleanOperation ')'
     | NEG booleanOperation
     ;

var: ID (':' type)?
        ;
value: INT #int
     | REAL #real
     | ID   #id
     | BOOL #bool
     | STRING #string
     | ID ('[' INT ']') #arrayAccess
     ;
type: 'i8'
    | 'i16'
    | 'i32'
    | 'i64'
    | 'f64'
    | 'f32'
    | 'bool'
    | 'str'
    ;


AND     : 'and';
OR      : 'or';
XOR     : 'xor';
NEG     : 'neg';
READ    : 'read';
PRINT   : 'print';
BOOL    : 'true' | 'false';
WS : [\r\n \t]+ -> skip;
INT     : [0-9]+ ;
REAL   : [0-9]+ '.' [0-9]+;
ID      : [a-zA-Z0-9]+;
ADD     : '+';
MULT    : '*';
DIV     : '/';
SUB     : '-';
STRING : '"' [a-zA-Z0-9 \t\n*+-]+ '"';
        


