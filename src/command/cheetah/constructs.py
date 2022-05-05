




CH_OPEN_CONDITIONAL = set(['#if ', '#unless '])
CH_WITHIN_CONDITIONAL = set(['#else if ', '#elif ', '#else'])
CH_CLOSE_CONDITIONAL = set(['#end if', '#end unless'])
CH_ALL_CONDITIONAL = CH_OPEN_CONDITIONAL | CH_WITHIN_CONDITIONAL | CH_CLOSE_CONDITIONAL

CH_OPEN_LOOP = set(['#for ', '#while '])
CH_CLOSE_LOOP = set(['#end for', '#end while'])
CH_ALL_LOOP = CH_OPEN_LOOP | CH_CLOSE_LOOP

CH_TRY_EXCEPT = set(['#try ', '#except', '#end try'])

CH_OPEN_FUNC = set(['#def '])
CH_CLOSE_FUNC = set(['#end def'])
CH_ALL_FUNC = CH_OPEN_FUNC | CH_CLOSE_FUNC

CH_ENV = set(['#set ', '#import ', '#from ', '#silent ', '#echo '])

LINUX_ALIAS = set(['set ', 'ln ', 'cp ', 'mv ', 'export '])
LINUX_CMD = set(['mkdir ', 'tar ', 'ls ', 'head ', 'wget ', 'grep ', 'awk ', 'cut ', 'sed ', 'gzip ', 'gunzip ', 'cd ', 'echo ', 'trap ', 'touch '])

CH_CONSTRUCTS = CH_ALL_CONDITIONAL | CH_ALL_LOOP | CH_ALL_FUNC | CH_TRY_EXCEPT | CH_ENV
