MAKEFILE DEFAULTS:
```
DEST_DIR ?= "/usr/local/memcached"
WATCH_DIRECTORY ?= "."
MEMCACHED_SERVER ?= "127.0.0.1:11211"
INTERVAL ?= 60
LOGFILE ?= "memsister.log"
SKIP_PIP ?= 0
```

Requirements:
Python3.8
Memcached
cacheFiles with list of keys|values

--- 
Struct of memcahced kv pair
`nameOfFile_key = values`

---
Struct of cacheFile.base
`key|values`

---
INSTALL on destination system

`make install`

Install without pip 

`make install SKIP_PIP=1`

Update env file 

`make update-env-file`

Specify env file values 

`make install WATCH_DIRECTORY=.MEMCACHED_SERVER=127.0.0.1:11211 INTERVAL=60 LOGFILE=memsister.log` 

or

`make update-env-file WATCH_DIRECTORY=. MEMCACHED_SERVER=127.0.0.1:11211 INTERVAL=60 LOGFILE=memsister.log`

IMPORTANT

DEST_DIR - Should point to memcached install directory. If you decide to use diffrent 
than default directory, you need always specify `make target DEST_DIR=/path/to/dir`

And update memsister.service accordingly