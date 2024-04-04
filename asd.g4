grammar asd;
prog:  expr*  EOF ;
expr: value ADD value #add
    | ID '=' (value | expr) #assign
    | PRINT '(' value ')' #print
    | READ '(' ID ')' #read
    | value MULT value #mult
    | value DIV value #div
    | value SUB value #sub
    ;
value: INT #int
     | REAL #real
     | ID   #id
     ;

READ    : 'read';
PRINT   : 'print';
WS : [\r\n \t]+ -> skip;
INT     : [0-9]+ ;
REAL   : [0-9]+ '.' [0-9]+;
ID      : [a-zA-Z0-9]+;
ADD     : '+';
MULT    : '*';
DIV     : '/';
SUB     : '-';



