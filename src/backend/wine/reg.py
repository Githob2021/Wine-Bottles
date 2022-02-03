import os
import uuid
from typing import NewType

from bottles.backend.logger import Logger # pyright: reportMissingImports=false
from bottles.backend.wine.wineprogram import WineProgram
from bottles.backend.wine.winedbg import WineDbg
from bottles.backend.utils.manager import ManagerUtils

logging = Logger()

# Define custom types for better understanding of the code
BottleConfig = NewType('BottleConfig', dict)


class Reg(WineProgram):
    program = "WINE Registry CLI"
    command = "reg"

    def add(self, key: str, value: str, data: str, keyType: str=False):
        config = self.config
        logging.info(
            f"Adding Key: [{key}] with Value: [{value}] and "
            f"Data: [{data}] in {config['Name']} registry"
        )
        winedbg = WineDbg(config)
        args = "add '%s' /v '%s' /d '%s' /f" % (key, value, data)
        
        if keyType:
            args = "add '%s' /v '%s' /t %s /d '%s' /f" % (
                key, value, keyType, data
            )
        
        # avoid conflicts when executing async
        winedbg.wait_for_process("reg.exe")
        
        res = self.launch(args, comunicate=True)
        logging.info(res)
        
    def remove(self, key: str, value: str):
        '''
        This function remove a value with its data in the given
        bottle registry key.
        '''
        config = self.config
        logging.info(
            f"Removing Value: [{key}] from Key: [{value}] in "
            f"{config['Name']} registry"
        )
        winedbg = WineDbg(config)
        args = "delete '%s' /v %s /f" % (key, value)

        # avoid conflicts when executing async
        winedbg.wait_for_process("reg.exe")

        res = self.launch(args, comunicate=True)
        logging.info(res)
    
    def import_bundle(self, bundle: dict):
        '''
        This function import a bundle to the given bottle registry.
        '''
        config = self.config
        logging.info(
            f"Importing bundle to {config['Name']} registry"
        )
        winedbg = WineDbg(config)
        reg_file = ManagerUtils.get_temp_path(f"{uuid.uuid4()}.reg")
        
        # prepare reg file
        with open(reg_file, "w") as f:
            f.write("REGEDIT4\n\n")

            for key in bundle:
                f.write(f"[{key}]\n")

                for value in bundle[key]:
                    if "keyType" in value:
                        f.write(f'"{value["value"]}"={value["keyType"]}:{value["data"]}\n')
                    else:
                        f.write(f'"{value["value"]}"="{value["data"]}"\n')

                f.write("\n")
            
        args = f"import {reg_file}"

        # avoid conflicts when executing async
        winedbg.wait_for_process("reg.exe")

        res = self.launch(args, comunicate=True)
        logging.info(res)

        # remove reg file
        os.remove(reg_file)
