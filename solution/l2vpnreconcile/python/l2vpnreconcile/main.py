# -*- mode: python; python-indent: 4 -*-

import ncs
from ncs.application import Service
from ncs.dp import Action
import random
import _ncs

class Reconcile(Action):
  
  def getDevice(self,name, root):
    if root.devices is None or name is None:
      return None
    for device in root.devices.device:
      if name == device.name:
        return device
    return None

  def getRs(self):        
    return str(random.randint(1, 1500))
     
  def redeploySrs(self,root, srs):
    self.log.info('Executing redeplySrs(...)')
    if srs is None or len(srs) == 0:
      return
    for sr in srs:
      # action = root.services.L2Vpn[sr].un_deploy
      # self.log.info('undeploy %s' %sr)
      # input = action.get_input()
      # ignore = input.ignore_refcount.create()
      # output = action(ignore)
      action = root.services.L2Vpn[sr].re_deploy
      input = action.get_input()
      reconcile = input.reconcile.create()
      self.log.info('perform redploy %s' %sr)
      output = action(reconcile) 
       
  def isDryRunEmpty(self,root):
    input = root.services.commit_dry_run.get_input()
    input.outformat = "native"
    result = root.services.commit_dry_run(input)
    for dvc in result.native.device:
      if dvc.data is not None:
        return False
    return True
      

  @Action.action

  def cb_action(self, uinfo, name, kp, input, output):
    pe_device = ''
    srs = []
    self.log.info('start reconcile')
    with ncs.maapi.Maapi() as m:
      with ncs.maapi.Session(m, uinfo.username, uinfo.context):
        with m.start_write_trans() as t:
          try:  

            root = ncs.maagic.get_root(t) 
            pe_device = self.getDevice(input.device_name, root);
            
            if pe_device is None:
              output.success = False
              output.message = 'device ' + input.device_name + 'not in system'
              return           
            message = pe_device.sync_from()
            int_path = '/ncs:devices/ncs:device{%s}/config/cisco-ios-xr:interface/Bundle-Ether-subinterface/Bundle-Ether' %input["device-name"]        
            if t.exists(int_path):
              bundleEths = ncs.maagic.get_node(t,int_path)
              if len(bundleEths) == 0:
                output.success = True
                output.message = "finish reconcile"  
                return    
              for bundleEther in bundleEths:
                id , bstag = bundleEther.id.split('.')
                description = bundleEther.description
                stags = bundleEther.encapsulation.dot1q.vlan_id              
                if stags is  None or len(stags)==0:
                  continue 
                stag = 0
                for stag in stags: 
                  if int(stag) == int(bstag):                 
                    break
                if stag == 0:
                  self.log.warning('vlan tag not configured, or does not match sub-interface id for Bundle-Ether-subinterface %s, use sub-interface id'%bundleEther.id)

                order_number = ''
                customer = ''
                if description is None:
                  order_number = self.getRs()
                  customer = 'ciscolive'
                  sr_name = 'reconcile-'+ customer + '-'+order_number
                else:
                  sr_name = description + '-'  + input.device_name
                  customer,order_number = description.split('-')
                sr_path = 'ncs:services/L2Vpn:L2Vpn{%s}' %(sr_name)
                if t.exists(sr_path):
                    self.log.info('sr ' + sr_name + 'exists, skipping')
                    continue
                sr_node = ncs.maagic.get_node(t, "/ncs:services/L2Vpn:L2Vpn")
                obj = sr_node.create(sr_name)
                obj.order_number = order_number
                obj.customer_name = customer
                pe_path = sr_path + '/pe-devices'
                pes_node = ncs.maagic.get_node(t,pe_path)
                pe_obj = pes_node.create(input.device_name)
                pe_obj.stag = bstag
                pe_obj.Bundle_Ether = id
                srs.append(sr_name) 
                           
            if len(srs) > 0:
              if not self.isDryRunEmpty(root):                 
                output.success = False
                output.message = 'commit dry-run output not empty, stop reconcilation'
                
              t.apply(flags=_ncs.maapi.COMMIT_NCS_NO_NETWORKING)
              message = pe_device.sync_from()
              self.redeploySrs(root,srs)
              output.success = True
              output.message = "Successfully created the services."
              
          except Exception as e:
            self.log.error(str(e))
            output.success = False
            output.message = str(e)

          finally:
            self.log.info('Context: %s' % uinfo.context)

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_action('reconcile', Reconcile)
    def teardown(self):
        self.log.info('Main FINISHED')

