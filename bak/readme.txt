.\ParserService\py2env\bin\activate.csh		需要修改py2env/bin下的activate路径，因为它生成的是绝对路径。注意linux和windows是不一样的,windows需要用"\\"来取代原有的路径"\"符

例如:
windows:

setenv VIRTUAL_ENV "D:\\work\\python_prj\\FireWarningParserService\\ParserService\\py2env"

Linux:

setenv VIRTUAL_ENV "/home/steven/src/ParserService/py2env"