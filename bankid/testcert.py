#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
:mod:`bankid`
==================

.. module:: bankid
   :platform: Unix, Windows
   :synopsis:

.. moduleauthor:: hbldh <henrik.blidh@nedomkull.com>

Created on 2014-09-09, 16:55

"""

from __future__ import division
from __future__ import print_function
from __future__ import absolute_import

import os
import re
import tempfile
import subprocess
import sys
import requests

_TEST_CERT_PASSWORD = 'qwerty123'
_CERT_URL = "http://www.bankid.com/Global/wwwbankidcom/RP/FPTestcert1.pfx"


def create_test_server_cert_and_key(destination_path):
    """Fetch the Pfx certificate from BankID servers, split it into
    a certificate part and a key part and save them as separate files,
    stored in PEM format.

    :param destination_path: The directory to save certificate and key to.
    :type destination_path: unicode
    :returns: The path tuple ``(cert_path, key_path)``.
    :rtype: tuple

    """
    if sys.platform == 'win32':
        raise NotImplementedError(
            "Test certificate fetching in Windows not supported. "
            "See documentation for details.")

    # Paths to temporary files.
    cert_tmp_path = os.path.abspath(
        os.path.join(tempfile.gettempdir(),
                     os.path.basename(_CERT_URL)))
    conv_tmp_path = os.path.abspath(
        os.path.join(tempfile.gettempdir(),
                     'certificate.pem'))

    # Paths to output files.
    out_cert_path = os.path.abspath(
        os.path.join(os.path.abspath(destination_path),
                     'cert.pem'))
    out_key_path = os.path.abspath(
        os.path.join(os.path.abspath(destination_path),
                     'key.pem'))

    # Fetch pfx certificate and store in temporary folder.
    r = requests.get(_CERT_URL)
    with open(cert_tmp_path, 'wb') as f:
        f.write(r.content)

    # Use openssl for converting to pem format.
    pipeline_1 = [
        'openssl', 'pkcs12',
        '-in', "{0}".format(cert_tmp_path),
        '-passin', 'pass:{0}'.format(_TEST_CERT_PASSWORD),
        '-out', "{0}".format(conv_tmp_path),
        '-passout', 'pass:{0}'.format(_TEST_CERT_PASSWORD)]
    p = subprocess.Popen(pipeline_1, stdout=subprocess.PIPE)
    p.communicate()

    # Open the newly created pem certificate in temporary folder.
    with open(conv_tmp_path, 'rt') as f:
        cert_and_key = f.read()

    # Split it into a certificate part and a private key part.
    # Save these parts to separate files.
    s = re.search('-----END CERTIFICATE-----', cert_and_key)
    certificate = cert_and_key[:s.end()]
    key = cert_and_key[s.end():]

    with open(out_cert_path, 'wt') as f:
        f.write(certificate)
    with open(out_key_path, 'wt') as f:
        f.write(key)

    # Try to remove all temporary files.
    try:
        os.remove(cert_tmp_path)
        os.remove(conv_tmp_path)
    except:
        pass

    # Return path tuples.
    return out_cert_path, out_key_path


def main():
    paths = create_test_server_cert_and_key(os.path.expanduser('~'))
    print('Saved cerificate as {0}'.format(paths[0]))
    print('Saved key as {0}'.format(paths[1]))

if __name__ == "__main__":
    main()
