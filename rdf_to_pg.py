# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 19:18:24 2018

@author: Joan Plepi
"""

from converter import Converter


if __name__ == "__main__":
    convert = Converter("northwind.data.v1.nt")
    convert.execute()