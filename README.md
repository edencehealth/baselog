# baselog

`baselog` is a Python module intended to simplify and standardize logging in our Python applications, particularly Dockerized applications. It is simply a thin wrapper around the stdlib [logging](https://docs.python.org/3/library/logging.html) module.

Many of our codebases are containerized and have the following operational requirements:
* Log messages get logged to the standard error (in agreement with the [12 factor](https://12factor.net/) design principles)
* If a `log_dir` path is supplied, a new log file is also created in that directory for every run of the app
* All uncaught exceptions are logged as described above
* Standard timezone-aware formats for log messages and timestamps

## Example

In the main file in an application, `BaseLog` is used to initialize both the console and file loggers.

```python
#!/usr/bin/env python3
from baselog import BaseLog

from .util import otherfunc


logger = BaseLog(
    __package__,
    log_dir="/logs",
    console_log_level="DEBUG",
    file_log_level="DEBUG",
)

def main():
    logger.info("starting a thing")
    otherfunc()

if __name__ == '__main__':
    main()
```

In other files of the project you just import the standard python logging module and get a logger.

```python
#!/usr/bin/env python3

import logging

logger = logging.getLogger(__name__)


def otherfunc():
    logger.warning("Log 'em'!")
```

A `sys.excepthook` is set by `BaseLog`, so in the case of an uncaught exception, the exception and traceback are logged to the console and log files:

```log
2023-04-11T20:06:59+0000 - logdemo - INFO - starting a thing
2023-04-11T20:06:59+0000 - logdemo.util - WARNING - Things may be happening
2023-04-11T20:06:59+0000 - logdemo.other.funcs - INFO - Things aren't happening yet
2023-04-11T20:06:59+0000 - logdemo - CRITICAL - uncaught exception: RuntimeError; What the crap!
2023-04-11T20:06:59+0000 - logdemo - CRITICAL - traceback-000: Traceback (most recent call last):
2023-04-11T20:06:59+0000 - logdemo - CRITICAL - traceback-001:   File "<frozen runpy>", line 198, in _run_module_as_main
2023-04-11T20:06:59+0000 - logdemo - CRITICAL - traceback-002:   File "<frozen runpy>", line 88, in _run_code
2023-04-11T20:06:59+0000 - logdemo - CRITICAL - traceback-003:   File "/app/logdemo/__main__.py", line 21, in <module>
2023-04-11T20:06:59+0000 - logdemo - CRITICAL - traceback-004:     main()
2023-04-11T20:06:59+0000 - logdemo - CRITICAL - traceback-005:   File "/app/logdemo/__main__.py", line 17, in main
2023-04-11T20:06:59+0000 - logdemo - CRITICAL - traceback-006:     whatsit()
2023-04-11T20:06:59+0000 - logdemo - CRITICAL - traceback-007:   File "/app/logdemo/other/funcs.py", line 10, in whatsit
2023-04-11T20:06:59+0000 - logdemo - CRITICAL - traceback-008:     raise RuntimeError("What the heck?!")
2023-04-11T20:06:59+0000 - logdemo - CRITICAL - traceback-009: RuntimeError: What the heck?!
```
