# importer.py
#
# Copyright 2020 brombinmirko <send@mirko.pm>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import yaml
import subprocess
from glob import glob
from datetime import datetime

from bottles.backend.logger import Logger # pyright: reportMissingImports=false
from bottles.backend.globals import TrdyPaths, Paths
from bottles.backend.models.samples import Samples
from bottles.backend.models.result import Result


logging = Logger()

class ImportManager:

    def __init__(self, manager):
        self.manager = manager

    def search_wineprefixes(self) -> list:
        importer_wineprefixes = []

        # search wine prefixes in external managers paths
        lutris_results = glob(f"{TrdyPaths.lutris}/*/")
        playonlinux_results = glob(f"{TrdyPaths.playonlinux}/*/")
        bottlesv1_results = glob(f"{TrdyPaths.bottlesv1}/*/")

        results = lutris_results + playonlinux_results + bottlesv1_results

        # count results
        is_lutris = len(lutris_results)
        is_playonlinux = len(playonlinux_results)
        i = 1

        for wineprefix in results:
            wineprefix_name = wineprefix.split("/")[-2]

            # identify manager by index
            if i <= is_lutris:
                wineprefix_manager = "Lutris"
            elif i <= is_playonlinux:
                wineprefix_manager = "PlayOnLinux"
            else:
                wineprefix_manager = "Bottles v1"

            # check the drive_c path exists
            if os.path.isdir(f"{wineprefix}/drive_c"):
                wineprefix_lock = os.path.isfile(f"{wineprefix}/bottle.lock")
                importer_wineprefixes.append(
                    {
                        "Name": wineprefix_name,
                        "Manager": wineprefix_manager,
                        "Path": wineprefix,
                        "Lock": wineprefix_lock
                    })
            i += 1

        logging.info(f"Found {len(importer_wineprefixes)} wineprefixes…")

        return Result(
            status=True,
            data={
                "wineprefixes": importer_wineprefixes
            }
        )

    def import_wineprefix(self, wineprefix: dict) -> bool:
        '''
        This function imports a wineprefix from an external wineprefix
        manager and converts it into a bottle. It also creates a lock file
        in the source path to prevent multiple imports.
        '''
        logging.info(
            f"Importing wineprefix [{wineprefix['Name']}] in a new bottle…"
        )

        # prepare bottle path for the wine prefix
        bottle_path = "Imported_%s" % wineprefix.get("Name")
        bottle_complete_path = "%s/%s" % (Paths.bottles, bottle_path)

        try:
            os.makedirs(bottle_complete_path, exist_ok=False)
        except:
            logging.error(
                "Error creating bottle path for wineprefix "
                f"[{wineprefix['Name']}], aborting."
            )
            return Result(False)

        # create lockfile in source path
        logging.info("Creating lock file in source path…")
        open(f'{wineprefix.get("Path")}/bottle.lock', 'a').close()

        # copy wineprefix files in the new bottle
        command = f"cp -a {wineprefix.get('Path')}/* {bottle_complete_path}/"
        subprocess.Popen(command, shell=True).communicate()

        # create bottle config
        new_config = Samples.config
        new_config["Name"] = wineprefix["Name"]
        new_config["Runner"] = self.manager.get_latest_runner()
        new_config["Path"] = bottle_path
        new_config["Environment"] = "Custom"
        new_config["Creation_Date"] = str(datetime.now())
        new_config["Update_Date"] = str(datetime.now())

        # save config
        with open(f"{bottle_complete_path}/bottle.yml", "w") as conf_file:
            yaml.dump(new_config, conf_file, indent=4)
            conf_file.close()

        # update bottles view
        self.manager.update_bottles(silent=True)

        logging.info(
            f"Wineprefix: [{wineprefix['Name']}] imported!"
        )
        return Result(True)