#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import logging
from utils import utils
from quart import Quart
from quart import jsonify


logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='error.log',
                    datefmt='%d-%b-%y %H:%M:%S')


app = Quart(__name__)


@app.route('/')
async def index():
    try:
        response = await utils.get_url_list()

        if response:
            return jsonify(response), 200
        else:
            return jsonify([{'done': True}]), 204

    except Exception as error:
        print(f'ERROR: {error}. Check error.log for tracestack.')
        sys.exit(1)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
