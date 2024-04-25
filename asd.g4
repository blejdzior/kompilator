grammar asd;
prog:  expr*  EOF ;
expr: value ADD value #add
    | var '=' matAss #matrixAssign
    | var '=' arrAss #arrayAssign
    | var '=' (value | expr) #assign
    | ID ('[' INT ']') '=' (value | expr) #elementAssign
    | ID '[' INT ']' '[' INT ']' '=' (value | expr) #matrixElementAssign
    | PRINT '(' value ')' #print
    | READ '(' ID ')' #read
    | value MULT value #mult
    | value DIV value #div
    | value SUB value #sub
    | booleanOperation # booleanOp
    | IF '(' equal ')' '{' blockif '}' #if
    | REPEAT repsNr '{' blockwhile '}' #repeat
    | PRINTGEN '(' genPrintId ')'   #printGen
    | FOR ID 'in' genCallId '()' '{' blockfor '}' #forGen
    | FUNCTION funType funId '{' blockfun '}' #function
    | GENERATOR genType genId '{' blockGen '}' #generator
    | STRUCT structId '{' blockstruct '}' #struct
    | CLASS classId '{' blockclass '}' #class
    | var '=' STRUCT structId #structAssign
    | var '=' CLASS classId #classAssign
    | ID '.' var #memberAccess
    | ID '.' var '=' value #memberAssign
    | ID '.' var '()' #methodCall
    ;

genPrintId: ID;
genCallId: ID;
blockfor: expr*;
genType: type;
genId: ID;
blockGen: (expr | yieldExpr)*;
yieldExpr: YIELD value;
structId: ID;
classId : ID;
blockclass: declaration* method*;
method: methodType methodId '{' blockmethod '}'
        ;
blockmethod: expr*;
methodType: type;
methodId: ID;

blockstruct: declaration*;
declaration: var # varDeclaration
           ;
funId: ID;
funType: type;
blockfun: expr*;
repsNr: ID | INT;
blockwhile: expr* ;
equal: ID '==' INT;
blockif: expr* ;

booleanOperation: andOp # and
                | orOp # or
                | xorOp # xor
                | negOp # neg
                ;
matAss: '[' matLine* ']' # matrix
      ;
matLine: value+ SEMI? #matrixLine;

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
     | ID '[' INT ']' '[' INT ']' #matrixAccess
     | ID '()' #call
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

PRINTGEN: 'printgen';
FOR     : 'for';
GENERATOR: 'gen';
YIELD   : 'yield';
STRUCT  : 'struct';
CLASS   : 'class';
FUNCTION: 'fun';
IF      : 'if';
REPEAT  : 'repeat';
AND     : 'and';
OR      : 'or';
XOR     : 'xor';
NEG     : 'neg';
READ    : 'read';
PRINT   : 'print';
BOOL    : 'true' | 'false';
SEMI    : ';';
WS : [\r\n \t]+ -> skip;
INT     : [0-9]+ ;
REAL   : [0-9]+ '.' [0-9]+;
ID      : [a-zA-Z0-9]+;
ADD     : '+';
MULT    : '*';
DIV     : '/';
SUB     : '-';
STRING : '"' [a-zA-Z0-9 \t\n*+-]+ '"';
        


