import os
import sys
import asyncio
import logging
import pymysql.cursors


num_of_urls = int(os.environ.get('NUMBER_OF_URLS', 300))
url_num_low = 1


async def get_url_list():
    global url_num_low
    url_num_high = url_num_low + num_of_urls - 1

    db = os.environ.get('MYSQL_DATABASE')
    host = os.environ.get('MYSQL_HOST')
    port = int(os.environ.get('MYSQL_PORT'))
    user = os.environ.get('MYSQL_USER')
    password = os.environ.get('MYSQL_PASSWORD')

    connection = pymysql.connect(host=host,
                                 port=port,
                                 user=user,
                                 password=password,
                                 db=db,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            sql = 'SELECT `ID`, `part_name`, `part_url` FROM `crawler_parts` \
                   WHERE `ID` BETWEEN %s AND %s'

            cursor.execute(sql, (str(url_num_low), str(url_num_high)))
            result = cursor.fetchall()
            url_num_low = url_num_high + 1

            return result

    except pymysql.err.MySQLError:
        raise

    finally:
        if connection:
            connection.close()
