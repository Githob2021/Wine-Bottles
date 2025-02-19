# generic.py
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

import re
import sys

from datetime import datetime


def validate_url(url: str):
    '''
    This function validates a given URL.
    It returns True if the URL is valid, False otherwise.
    '''
    regex = re.compile(
        r'^(?:http|ftp)s?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$',
        re.IGNORECASE
    )

    return re.match(regex, url) is not None


def detect_encoding(text: bytes):
    '''
    This function detects the encoding of a given file.
    It returns the encoding if it is valid, None otherwise.
    '''
    encodings = [
        sys.stdout.encoding,
        "ascii",
        "utf-8",
        "utf-16",
        "utf-32",
        "latin-1",
        "big5",
        "gb2312",
        "gb18030",
        "euc_jp",
        "euc_jis_2004",
        "euc_jisx0213",
        "shift_jis",
        "shift_jis_2004",
        "shift_jisx0213",
        "iso2022_jp",
        "iso2022_jp_1",
        "iso2022_jp_2",
        "iso2022_jp_2004",
        "iso2022_jp_3",
        "iso2022_jp_ext",
        "iso2022_kr",
        "utf_32_be",
        "utf_32_le",
        "utf_16_be",
        "utf_16_le",
        "utf_7",
        "utf_8_sig",
        "utf_16_be_sig",
        "utf_16_le_sig",
        "utf_32_be_sig",
        "utf_32_le_sig"
    ]

    for encoding in encodings:
        try:
            text.decode(encoding)
            return encoding
        except UnicodeDecodeError:
            pass

    return None