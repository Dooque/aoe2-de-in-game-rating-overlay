"""
A simple and basic Python 3 https://aoe2.net/ API wrapper for sending `GET requests`.

Available on GitHub (+ documentation): https://github.com/sixP-NaraKa/aoe2net-api-wrapper

Additional data manipulation/extraction from the provided data by this API wrapper has to be done by you, the user.

See https://aoe2.net/#api & https://aoe2.net/#nightbot.

MIT License. See `__license__` for more information.
"""

from sys import version_info

if version_info.major < 3:
    raise Exception("Python 3.X required.")

# import the needed classes (also the custom exception)
from .aoe2 import API, Nightbot, Aoe2NetException

__version__ = "1.1.0"
__license__ = """
MIT License

Copyright (c) 2021 sixP-NaraKa

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
