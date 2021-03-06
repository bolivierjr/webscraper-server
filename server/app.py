#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging
from utils import utils
from quart import Quart, request, jsonify, render_template


timeout = int(os.environ.get('SCRAPE_TIMEOUT', 3))
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='master.log',
                    datefmt='%d-%b-%y %H:%M:%S')

app = Quart(__name__)


@app.route('/status')
async def index():
    try:
        progress = await utils.get_progress()

        return await render_template('index.html', progress=progress), 200

    except Exception as error:
        logging.error(f'{error}', exc_info=True)
        print(f'ERROR: {error}. Check master.log for tracestack.')

        return jsonify([{'error': 'Oops, having a problem'}]), 500


@app.route('/api/get_ip', methods=['GET'])
async def ip():
    try:
        return jsonify({'ip': request.access_route[0]}), 200

    except Exception as error:
        logging.error(f'{error}', exc_info=True)
        print(f'ERROR: {error}. Check master.log for tracestack.')

        return jsonify([{'error': 'Oops, having a problem'}]), 500


@app.route('/api/urls', methods=['GET'])
async def urls():
    try:
        response = await utils.get_url_list()

        if response:
            response.append({'timeout': timeout})

            return jsonify(response), 200

        else:
            return jsonify([{'done': True}]), 200

    except Exception as error:
        logging.error(f'{error}', exc_info=True)
        print(f'ERROR: {error}. Check master.log for tracestack.')

        return jsonify([{'error': 'Oops, having a problem'}]), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5000')
