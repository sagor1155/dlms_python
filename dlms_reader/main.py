#
#  --------------------------------------------------------------------------
#   Gurux Ltd
#
#
#
#  Filename: $HeadURL$
#
#  Version: $Revision$,
#                   $Date$
#                   $Author$
#
#  Copyright (c) Gurux Ltd
#
# ---------------------------------------------------------------------------
#
#   DESCRIPTION
#
#  This file is a part of Gurux Device Framework.
#
#  Gurux Device Framework is Open Source software; you can redistribute it
#  and/or modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2 of the License.
#  Gurux Device Framework is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#  See the GNU General Public License for more details.
#
#  More information of Gurux products: http://www.gurux.org
#
#  This code is licensed under the GNU General Public License v2.
#  Full text may be retrieved at http://www.gnu.org/licenses/gpl-2.0.txt
# ---------------------------------------------------------------------------
import sys
import time
import traceback
from gurux_common.io import Parity, StopBits, BaudRate
from gurux_serial import GXSerial
from gurux_net import GXNet
from gurux_dlms.enums import ObjectType
from GXSettings import GXSettings
from GXDLMSReader import GXDLMSReader

#pylint: disable=too-few-public-methods,broad-except
class sampleclient():
    @classmethod
    def main(cls, args):
        # args: the command line arguments
        reader = None
        settings = GXSettings()
        try:
            # //////////////////////////////////////
            #  Handle command line parameters.
            # ret = settings.getParameters(args)
            ret = settings.get_fixed_config_parameters()
            if ret != 0:
                return
            
            # //////////////////////////////////////
            #  Initialize connection settings.
            if isinstance(settings.media, GXSerial):
                #print ('Using Serial port Media')
                if settings.iec:
                    #settings.media.port = '/dev/ttyUSB0'
                    settings.media.baudrate = BaudRate.BAUD_RATE_300
                    settings.media.bytesize = 7
                    settings.media.parity = Parity.EVEN
                    settings.media.stopbits = StopBits.ONE
                else:
                    #settings.media.port = '/dev/ttyUSB0'
                    settings.media.baudrate = BaudRate.BAUD_RATE_9600
                    settings.media.bytesize = 8
                    settings.media.parity = Parity.NONE
                    settings.media.stopbits = StopBits.ONE
                    print (settings.media.port)
                    print (settings.media.baudRate)

            elif not isinstance(settings.media, GXNet):
                raise Exception("Unknown media type.")
            # //////////////////////////////////////
            reader = GXDLMSReader(settings.client, settings.media, settings.trace)
            
            # print('------------------------------------------------------------')
            # print ('Send SNRM and AARQ')
            # print('------------------------------------------------------------')
            # reader.initializeConnection()
            # print('------------------------------------------------------------')           
        
            # print('Read Association View')
            # print('------------------------------------------------------------')
            # reader.getAssociationView()
            # print('------------------------------------------------------------')
            
            # reader.close()
            #obj_1 = ['0.0.1.0.0.255', 1]
            obj_2 = ['0.0.1.0.0.255', 2]
            #settings.readObjects.append(obj_1)
            settings.readObjects.append(obj_2)

            if settings.readObjects:
                print('------------------------------------------------------------')
                print ('Send SNRM and AARQ')
                print('------------------------------------------------------------')
                reader.initializeConnection()
                print('------------------------------------------------------------')
                print('Read Association View')
                print('------------------------------------------------------------')
                reader.getAssociationView()
                print('------------------------------------------------------------')
                
                for i in range(0, 2, 1):
                    val = reader.read(settings.client.objects.findByLN(ObjectType.NONE, '0.0.1.0.0.255'), 2)
                    reader.showValue(2, val)
                    time.sleep(2)

                count = 0
                while(count < 10):
                    settings.client.keepAlive()
                    time.sleep(3)
                    count += 1
                    
                # for k, v in settings.readObjects:
                #     val = reader.read(settings.client.objects.findByLN(ObjectType.NONE, k), v)
                #     print ('k: ' + str(k) + '  v: ' + str(v))
                #     reader.showValue(v, val)
                #     print('------------------------------------------------------------')

            else:
                reader.readAll()

        except Exception:
            traceback.print_exc()
        
        finally:
            if reader:
                try:
                    reader.close()
                except Exception:
                    traceback.print_exc()
            print("Ended. Press any key to continue.")

if __name__ == '__main__':
    sampleclient.main(sys.argv)
