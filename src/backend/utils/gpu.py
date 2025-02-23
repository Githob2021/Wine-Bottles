# gpu.py
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

import subprocess

from bottles.backend.utils.vulkan import VulkanUtils # pyright: reportMissingImports=false


class GPUUtils:

    __vendors = {
        "nvidia": "NVIDIA Corporation",
        "amd": "Advanced Micro Devices, Inc.",
        "intel": "Intel Corporation"
    }

    def __init__(self):
        self.vk = VulkanUtils()

    def list_all(self):
        found = []
        for _vendor in self.__vendors:
            _proc = subprocess.Popen(
                f"lspci | grep '{self.__vendors[_vendor]}'",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            stdout, stderr = _proc.communicate()

            if len(stdout) > 0:
                found.append(_vendor)
            
        return found
    
    def assume_discrete(self, vendors: list):
        if "nvidia" in vendors and "amd" in vendors:
            return {"integrated": "amd", "discrete": "nvidia"}
        elif "nvidia" in vendors and "intel" in vendors:
            return {"integrated": "intel", "discrete": "nvidia"}
        elif "amd" in vendors and "intel" in vendors:
            return {"integrated": "intel", "discrete": "amd"}
        return {}


    def get_gpu(self):
        checks = {
            "nvidia": {
                "query": "(VGA|3D).*NVIDIA"
            },
            "amd": {
                "query": "(VGA|3D).*AMD/ATI"
            },
            "intel": {
                "query": "(VGA|3D).*Intel"
            }
        }
        gpus = {
            "nvidia": {
                "vendor": "nvidia",
                "envs": {
                    "__NV_PRIME_RENDER_OFFLOAD": "1",
                    "__GLX_VENDOR_LIBRARY_NAME": "nvidia",
                    "__VK_LAYER_NV_optimus": "NVIDIA_only"
                },
                "icd": self.vk.get_vk_icd("nvidia", as_string=True)
            },
            "amd": {
                "vendor": "amd",
                "envs": {
                    "DRI_PRIME": "1"
                },
                "icd": self.vk.get_vk_icd("amd", as_string=True)
            },
            "intel": {
                "vendor": "intel",
                "envs": {
                    "DRI_PRIME": "1"
                },
                "icd": self.vk.get_vk_icd("intel", as_string=True)
            }
        }
        found = []
        result = {
            "vendors": {},
            "prime": {
                "integrated": None,
                "discrete": None
            }
        }

        for _check in checks:
            _query = checks[_check]["query"]
            _proc = subprocess.Popen(
                f"lspci | grep -iP '{_query}'",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )
            stdout, stderr = _proc.communicate()
            if len(stdout) > 0:
                found.append(_check)
                result["vendors"][_check] = gpus[_check]
        
        if len(found) >= 2:
            _discrete = self.assume_discrete(found)
            if _discrete:
                _integrated = _discrete["integrated"]
                _discrete = _discrete["discrete"]
                result["prime"]["integrated"] = gpus[_integrated]
                result["prime"]["discrete"] = gpus[_discrete]
        
        return result
