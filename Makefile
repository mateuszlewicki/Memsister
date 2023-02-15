SHELL=/bin/bash
DEST_DIR ?= /usr/local/memcached
WATCH_DIRECTORY ?= .
MEMCACHED_SERVER ?= 127.0.0.1:11211
INTERVAL ?= 60
LOGFILE ?= memsister.log
SKIP_PIP ?= 0

install: configure
	@echo "Installing Memsister in $(DEST_DIR)"
ifeq ($(SKIP_PIP),0)
	python3 -m pip install -r requirements.txt
else
	@echo "REMEMBER TO INSTALL PACKAGES SPECIFIED in requirements.txt"
	@cat requirements.txt
endif
	install -C -m 755 memsister.py $(DEST_DIR)/memsister
	install -C -m 644 memsister.env $(DEST_DIR)/memsister.env
	install -C -m 644 memsister.service /etc/systemd/system/memsister.service
	systemctl daemon-reload
	@echo "Installation complete."

configure: configure-env configure-systemd

configure-env:
	@echo "Generating memsister.env file"
	echo "_MEMSISTER_WATCH_DIRECTORY=$(WATCH_DIRECTORY)" > memsister.env
	echo "_MEMSISTER_MEMCACHED_SERVER=$(MEMCACHED_SERVER)" >> memsister.env
	echo "_MEMSISTER_INTERVAL=$(INTERVAL)" >> memsister.env
	echo "_MEMSISTER_LOGFILE=$(LOGFILE)" >> memsister.env
	@echo "Generation complete"

configure-systemd:
	@echo "Generating memsister.service file"
	sed -i 's!\(EnvironmentFile\)=/usr/local/memcached/memsister.env!\1=$(DEST_DIR)/memsister.env!' memsister.service 
	sed -i 's!\(ExecStart=/usr/bin/python3\) /usr/local/memcached/memsister!\1 $(DEST_DIR)/memsister!' memsister.service 
	@echo "Generation complete"

update-env-file: configure-env
	@echo "Updating $(DEST_DIR)/memsister.env file"
	install -C -m 644 memsister.env $(DEST_DIR)/memsister.env
	@echo "Update complete"

uninstall:
	@echo "Uninstalling Memsister from $(DEST_DIR)..."
	rm $(DEST_DIR)/memsister
	rm $(DEST_DIR)/memsister.env
	rm /etc/systemd/system/memsister.service
	systemctl daemon-reload
	@echo "Uninstallation complete."

.PHONY: uninstall update-env-file configure-env configure-systemd configure
