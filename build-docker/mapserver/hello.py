#!/usr/bin/env python

import cgitb
cgitb.enable()
print("Content-Type: text/html;charset=utf-8")

print "Content-type:text/html\r\n\r\n"
print '<html>'
print '<head>'
print '<title>Hello Word - First CGI Program</title>'
print '</head>'
print '<body>'
print '<h2>Hello Word! This is my first CGI program</h2>'
print '</body>'
print '</html>'