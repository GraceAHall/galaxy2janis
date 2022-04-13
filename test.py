
import shlex



test1 = 'READ_NAME_REGEX=\'${str ( $read_name_regex ) }\''
test2 = '"Module \'${repeat.software_cond.software}: \'$pattern\' not found in the file \'$identifier\'"'
test3 = 'READ_NAME_REGEX = \'${str ( $read_name_regex ) }\''
test4 = 'READ_NAME_REGEX = ${str ( $read_name_regex ) }'

print(shlex.split(test1))
print()
print(shlex.split(test2))
print()
print(shlex.split(test3))
print()
print(shlex.split(test4))
print()