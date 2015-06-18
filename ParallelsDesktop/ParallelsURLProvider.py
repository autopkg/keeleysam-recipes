#!/usr/bin/env python
#
# ParallelsURLProvider, version 2013.08.08
# Copyright 2013 Samuel Keeley, derived from BarebonesURLProvider by Timothy Sutton
# Thanks to Michael Lynn for help with xml.dom.minidom
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

import urllib2
import xml.dom.minidom
from distutils.version import LooseVersion
from operator import itemgetter

from autopkglib import Processor, ProcessorError

__all__ = ["ParallelsURLProvider"]

URLS = {
	"ParallelsDesktop6": "http://update.parallels.com/desktop/v6/en_us/parallels/parallels_updates.xml",
	"ParallelsDesktop7": "http://update.parallels.com/desktop/v7/parallels/parallels_updates.xml",
    "ParallelsDesktop8": "http://update.parallels.com/desktop/v8/parallels/parallels_updates.xml",
    "ParallelsDesktop9": "http://update.parallels.com/desktop/v9/parallels/parallels_updates.xml",
    "ParallelsDesktop10": "http://update.parallels.com/desktop/v10/parallels/parallels_updates.xml"
        }

class ParallelsURLProvider(Processor):
    description = "Provides a version, description, and DMG download for the Parallels product given."
    input_variables = {
        "product_name": {
        "required": True,
        "description": "Product to fetch URL for. One of 'ParallelsDesktop6', 'ParallelsDesktop7', 'ParallelsDesktop8', 'ParallelsDesktop9', 'ParallelsDesktop10'.",
        },
    }
    output_variables = {
        "version": {
            "description": "Version of the product.",
        },
        "url": {
            "description": "Download URL.",
        },
        "description": {
            "description": "Update description."
        }
    }
    __doc__ = description

    def main(self):

		def compare_version(a, b):
			return cmp(LooseVersion(a), LooseVersion(b))

		valid_prods = URLS.keys()
		prod = self.env.get("product_name")
		if prod not in valid_prods:
			raise ProcessorError("product_name %s is invalid; it must be one of: %s" % (
								prod, valid_prods))
		url = URLS[prod]
		try:
			manifest_str = urllib2.urlopen(url).read()
		except BaseException as e:
			raise ProcessorError("Unexpected error retrieving product manifest: '%s'" % e)

		the_xml = xml.dom.minidom.parseString(manifest_str)
		products = the_xml.getElementsByTagName('Product')
		parallels = None
		for a_product in products:
			# Find the products that are 'Parallels Desktop'
			if a_product.getElementsByTagName('ProductName')[0].firstChild.nodeValue == u'Parallels Desktop':
				parallels = a_product
				v_major         = parallels.getElementsByTagName('Major')[0].firstChild.nodeValue
				v_minor         = parallels.getElementsByTagName('Minor')[0].firstChild.nodeValue
				v_sub_minor     = parallels.getElementsByTagName('SubMinor')[0].firstChild.nodeValue
				v_sub_sub_minor = parallels.getElementsByTagName('SubSubMinor')[0].firstChild.nodeValue
				version = '.'.join([v_major, v_minor, v_sub_minor, v_sub_sub_minor])
				if prod != "ParallelsDesktop10":
					update = parallels.getElementsByTagName('Update')[0]
				else:
					update = parallels.getElementsByTagName('Update')[1]
				if prod != "ParallelsDesktop6":
					description = [x.firstChild.nodeValue for x in update.getElementsByTagName('UpdateDescription') if x.firstChild.nodeValue.startswith('en_US')][0]
					description = '<html><body>%s</body></html>' % (description.split('#',1)[-1])
				else:
					description = [x.firstChild.nodeValue for x in update.getElementsByTagName('UpdateDescription')][0]
				url = update.getElementsByTagName('FilePath')[0].firstChild.nodeValue

		self.env["version"] = version
		self.env["description"] = description
		self.env["url"] = url
		self.output("Found URL %s" % self.env["url"])

if __name__ == "__main__":
    processor = ParallelsURLProvider()
    processor.execute_shell()
