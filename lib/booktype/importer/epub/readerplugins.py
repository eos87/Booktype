# This file is part of Booktype.
# Copyright (c) 2013 Borko Jandras <borko.jandras@sourcefabric.org>
#
# Booktype is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Booktype is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Booktype.  If not, see <http://www.gnu.org/licenses/>.

import os
import urllib
import urlparse

import lxml
import lxml.html
from lxml import etree

import ebooklib

from ebooklib.plugins.base import BasePlugin
from ebooklib.utils import parse_html_string

from booktype.utils.tidy import tidy_cleanup

from ..utils import convert_file_name


class TidyPlugin(BasePlugin):
    NAME = 'Tidy HTML'
    OPTIONS = {#'utf8': None,
               'tidy-mark': 'no',
               'drop-font-tags': 'yes',
               'uppercase-attributes': 'no',
               'uppercase-tags': 'no',
               #'anchor-as-name': 'no',
              }

    def __init__(self, extra = {}):
        self.options = dict(self.OPTIONS)
        self.options.update(extra)

    def html_after_read(self, book, chapter):
        if not chapter.content:
            return None

        (_, chapter.content) = tidy_cleanup(chapter.content, **self.options)

        return chapter.content


    def html_before_write(self, book, chapter):
        if not chapter.content:
            return None

        (_, chapter.content) = tidy.tidy_cleanup(chapter.content, **self.options)

        return chapter.content


class ImportPlugin(BasePlugin):
    NAME = 'Import Plugin'

    def __init__(self, remove_attributes = None):
        if remove_attributes:
            self.remove_attributes = remove_attributes
        else:
            # different kind of onmouse
            self.remove_attributes = ['class', 'style', 'id', 'onkeydown', 'onkeypress', 'onkeyup',
                                      'onclick', 'ondblclik', 'ondrag', 'ondragend', 'ondragenter',
                                      'ondragleave', 'ondragover', 'ondragstart', 'ondrop',
                                      'onmousedown', 'onmousemove', 'onmouseout', 'onmouseover',
                                      'onmouseup', 'onmousewheel', 'onscroll']


    def after_read(self, book):
        # change all the file names for images
        #   - should fix if attachment name has non ascii characters in the name
        #   - should remove the space if file name has it inside

        for att in  book.get_items_of_type(ebooklib.ITEM_IMAGE):            
            att.file_name = convert_file_name(att.file_name)

    def html_after_read(self, book, chapter):
        try:
            tree = parse_html_string(chapter.content)
        except:
            return

        root = tree.getroottree()

        if len(root.find('head')) != 0:
            head = tree.find('head')
            title = head.find('title')

            if title is not None:
                chapter.title = title.text        

        if len(root.find('body')) != 0:
            body = tree.find('body')

            # todo:
            # - fix <a href="">
            # - fix ....

            for _item in body.iter():
                if _item.tag == 'img':
                    _name = _item.get('src')
                    # this is not a good check
                    if _name and not _name.lower().startswith('http'): 
                        _item.set('src', 'static/%s' % convert_file_name(_name))

                for t in self.remove_attributes:
                    if t in _item.attrib:
                        del _item.attrib[t]

        chapter.content = etree.tostring(tree, pretty_print=True, encoding='utf-8', xml_declaration=True)
