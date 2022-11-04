#!/usr/local/autopkg/python
#
# Copyright 2014 Nick Gamewell
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import

import re

from autopkglib import Processor, ProcessorError, URLGetter

__all__ = ["OperaURLProvider"]


BASE_URL = "https://get.geo.opera.com/ftp/pub/opera/desktop/"


class OperaURLProvider(URLGetter):
    """Provides a download URL for the latest Opera release."""

    input_variables = {
        "base_url": {"required": False, "description": "Default is %s" % BASE_URL,},
    }
    output_variables = {
        "url": {"description": "URL to the latest Opera release.",},
        "version": {"description": "Version of the latest Opera release.",},
    }
    description = __doc__

    def get_opera_url(self, url):
        version = None

        # Get list of links from directory listing
        page = self.download(url).decode('utf-8')
        links = re.findall(r'<a.*?\s*href="(.*?)".*?>', page)

        # Evaluate the links in reverse alphabetical order
        while True:
            curl_cmd = self.prepare_curl_cmd()
            curl_cmd.extend(["--head", url + max(links) + "mac/"])
            output = self.download_with_curl(curl_cmd)
            if "200 OK" in output:
                version = max(links).rstrip("/")
                break
            links.remove(max(links))
            if not links:
                raise ProcessorError("Did not find any valid versions to download.")

        # Obtain and return the dmg download URL and version
        url += max(links) + "mac/"
        page = self.download(url).decode('utf-8')
        links = re.findall(r'<a.*?\s*href="(.*?.dmg)".*?>', page)
        for link in links:
            if ".dmg" in link:
                url += link
        return url, version

    def main(self):
        """Find and return a download URL"""
        base_url = self.env.get("base_url", BASE_URL)
        self.env["url"], self.env["version"] = self.get_opera_url(base_url)
        self.output("Found URL %s" % self.env["url"])


if __name__ == "__main__":
    processor = OperaURLProvider()
    processor.execute_shell()
