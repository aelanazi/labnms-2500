# The order of packages is significant as there are dependencies between
# the packages. Typically generated namespaces are used by other packages.
PACKAGES = /home/nso/ncs-4.5.0.1/packages/neds/cisco-iosxr 
LAB_PACKAGES = /home/nso/packages/L2Vpn /home/nso/packages/l2vpnreconcile
# The create-network argument to ncs-netsim
NETWORK = create-network /home/nso/ncs-4.5.0.1/packages/neds/cisco-iosxr 3 asr9k 

NETSIM_DIR = /home/nso/ncs-run/netsim

all: build-all $(NETSIM_DIR)

lab: resetlab copylab all build-lab reload

build-all:
	for i in $(PACKAGES); do \
		$(MAKE) -C $${i}/src all || exit 1; \
	done
build-lab:
	for i in $(LAB_PACKAGES); do \
	    $(MAKE) -C $${i}/src clean all || exit 1; \
	done
$(NETSIM_DIR): 	
	ncs-netsim --dir $(NETSIM_DIR) $(NETWORK)
	cp /home/nso/initial-data/asr9k2-pre.xml /home/nso/ncs-run/netsim/asr9k/asr9k2/cdb/
	cp /home/nso/initial-data/asr9k1-pre.xml /home/nso/ncs-run/netsim/asr9k/asr9k1/cdb/
	cp /home/nso/initial-data/asr9k0-pre.xml /home/nso/ncs-run/netsim/asr9k/asr9k0/cdb/
	ncs-netsim --dir $(NETSIM_DIR) ncs-xml-init > /home/nso/ncs-run/ncs-cdb/netsim_devices_init.xml
reload:
	sh /home/nso/scripts/reload.sh
#Patch to add ios-stats
#packages/cisco-ios:
#	ln -s $(NCS_DIR)/packages/neds/cisco-ios packages/cisco-ios
#
#packages/juniper-junos:
#	ln -s $(NCS_DIR)/packages/neds/juniper-junos packages/juniper-junos
#
#packages/cisco-iosxr:
#	ln -s $(NCS_DIR)/packages/neds/cisco-iosxr packages/cisco-iosxr

clean:
	for i in $(PACKAGES); do \
		$(MAKE) -C $${i}/src clean || exit 1; \
	done
	rm -rf /home/nso/ncs-run/netsim /home/nso/ncs-run/running.DB /home/nso/ncs-run/logs/* /home/nso/ncs-run/state/* /home/nso/ncs-run/ncs-cdb/*.cdb /home/nso/ncs-run/*.trace
#	rm -f packages/cisco-ios
#	rm -f packages/juniper-junos
#	rm -f packages/cisco-iosxr
	rm -rf /home/nso/ncs-run/bin
	rm -rf /home/nso/ncs-run/ncs-cdb/*.xml

start:
	ncs-netsim --dir /home/nso/ncs-run/netsim start
	ncs --cd /home/nso/ncs-run

stop:
	-ncs-netsim --dir /home/nso/ncs-run/netsim stop
	-ncs --stop

reset:
	ncs-setup --reset
rmpackages:
	rm -rf ~/packages
	sh /home/nso/scripts/unlink.sh
cli:
	ncs_cli -u admin
resetlab: stop clean rmpackages all start
	sh /home/nso/scripts/sync.sh
copylab:
	sh /home/nso/scripts/copylab.sh
