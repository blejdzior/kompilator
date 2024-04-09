grammar asd;
prog:  expr*  EOF ;
expr: value ADD value #add
    | var '=' (value | expr) #assign
    | PRINT '(' value ')' #print
    | READ '(' ID ')' #read
    | value MULT value #mult
    | value DIV value #div
    | value SUB value #sub
    ;

var: ID (':' type)?
        ;
value: INT #int
     | REAL #real
     | ID   #id
     | BOOL #bool
     ;
type: 'i8'
    | 'i16'
    | 'i32'
    | 'i64'
    | 'f64'
    | 'f32'
    ;


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



