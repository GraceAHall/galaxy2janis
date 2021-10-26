

import re 
import numpy as np



the_string1 = 'hello ## there "yeah"'


the_string2 = """
hello \'##\' there "yeah"
"""


the_string3 = """
hello '##' there "yeah"
"""

the_string4 = """
## hello there "yeah"
"""



# find the areas of the string which are quoted
matches = re.finditer(r'"(.*?)"|\'(.*?)\'', the_string4)
quoted_sections = [(m.start(), m.end()) for m in matches]

# transform to mask
quotes_mask = np.zeros(len(the_string4))
for start, end in quoted_sections:
    quotes_mask[start: end] = 1

print(quotes_mask)

# find '##' 
matches = re.finditer('##', the_string4)
hash_hits = [(m.start(), m.end()) for m in matches]

# check each '##' to see if its quoted. if not, mark as start of comment
comment_start = -1
for start, end in hash_hits:
    if sum(quotes_mask[start: end]) == 0:
        comment_start = start
        break

# override line
line = the_string4[:comment_start]
print(line)
