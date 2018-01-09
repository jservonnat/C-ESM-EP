import os

from urllib import urlopen

# -> First, we read the template of the html file in share/fp_template
url = template
html = urlopen(template).read()

# -> Adding the links to the html lines
new_html_lines = html.splitlines()
for cesmep_module in cesmep_modules:
    newline = '<li><a href="target_'+cesmep_module[0]+'" target="_blank">'+cesmep_module[1]+'</a></li>'
    new_html_lines.append(newline)

# -> Add the end of the html file
new_html_lines = new_html_lines + ['','</body>','','</html>']

# -> We concatenate all the lines together
new_html = ''
for new_html_line in new_html_lines: new_html = new_html+new_html_line+'\n'

# -> Save as the html file that will be copied on the web server
main_html='C-ESM-EP_'+comparison+'.html'
with open(main_html,"w") as filout : filout.write(new_html)



