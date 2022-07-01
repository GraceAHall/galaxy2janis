


command: str
dev_test_cmdstrs: bool

# setting
def set_command(value: str) -> None:
    global command
    command = value

def set_outdir(value: str) -> None:
    global outdir
    outdir = value

def set_dev_test_cmdstrs(value: bool) -> None:
    global dev_test_cmdstrs
    dev_test_cmdstrs = value