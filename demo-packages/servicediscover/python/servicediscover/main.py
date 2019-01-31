# -*- mode: python; python-indent: 4 -*-

import ncs
from ncs.application import Service
from ncs.dp import Action
import random
import _ncs
import os

class DiscoverSr(Action):

  def validate_input(self,m,input):
    with m.start_read_trans() as t: 
      root = ncs.maagic.get_root(t)
      if root.devices is None or input.device_name is None:
        return False
      for device in root.devices.device:
        if input.device_name == device.name:
          return True
      return False
    
  # place holder for demo
  def perform_xslt(self,input):
    return True

  # place holder for demo

  def perform_import(self, m, input):
    return True
   
  # redeploy and reconcile
    
  def redeploySrs(self,root, srs):
    self.log.info('Executing redeplySrs(...)')
    if srs is None or len(srs) == 0:
      return
    for sr in srs:
      print(' ')
      action = sr.re_deploy
      input = action.get_input()
      reconcile = input.reconcile.create()
      self.log.info('perform redploy %s' %sr.sr_name)
      output = action(reconcile) 
      

  @Action.action

  def cb_action(self, uinfo, name, kp, input, output):
    pe_device = input.device_name
    action_name = input.action_name
    service_type = input.service_type
    discover_type = input.discover_type
    discover_result = True
    self.log.info('discover_type %s'  %discover_type)


    
    with ncs.maapi.Maapi() as m:
      with ncs.maapi.Session(m, uinfo.username, uinfo.context):        

        
        if self.validate_input(m,input):
          root = ncs.maagic.get_root(m)

          # inventory discovery
          syc_output = root.devices.device[pe_device].sync_from()

          #create service instances
          if discover_type == 'action':
            input = root.action[action_name].get_input()
            input.device_name = pe_device
            output = root.action[action_name](input)         
         
            if not output.success: 
              discover_result = False    


          elif discover_type == 'xslt':

            xslt_result = self.perform_xslt(input)

            if xslt_result:
              discover_result = self.perform_import(m, input)

          elif discover_type == 'attributes':
            discover_result = self.perform_import(m, input)

          if discover_result:
             # reset reference count to reconcile  
            with m.start_read_trans() as t:           
              t_root = ncs.maagic.get_root(t) 
              srs = t_root.services.L2Vpn              
              self.redeploySrs(t_root,srs)

          syc_output = root.devices.device[pe_device].sync_from()

   

class Main(ncs.application.Application):
    def setup(self):
        self.log.info('Main RUNNING')
        self.register_action('discover', DiscoverSr)
    def teardown(self):
        self.log.info('Main FINISHED')

