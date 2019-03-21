import os
import sys
import asyncio
import logging
import psycopg2
import pymysql.cursors


num_of_urls = os.environ.get('NUMBER_OF_URLS', 300)
url_num_low = 1

POSTGRES_HOST = os.environ.get('POSTGRES_HOST')
POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
POSTGRES_USER = os.environ.get('POSTGRES_USER')
POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
POSTGRES_DB = os.environ.get('POSTGRES_DB')

MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT'))
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')

psql_info = {
    'user': POSTGRES_USER,
    'password': POSTGRES_PASSWORD,
    'host': POSTGRES_HOST,
    'port': POSTGRES_PORT,
    'database': POSTGRES_DB,
}


async def get_url_list():
    global url_num_low
    url_num_high = url_num_low + num_of_urls - 1

    connection = pymysql.connect(host=MYSQL_HOST,
                                 user=MYSQL_USER,
                                 password=MYSQL_PASSWORD,
                                 db=MYSQL_DATABASE,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    sql = '''SELECT `ID`, `part_name`, `part_url` FROM `crawler_parts`
                      WHERE `ID` BETWEEN %s AND %s'''

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, (str(url_num_low), str(url_num_high)))
            result = cursor.fetchall()
            url_num_low = url_num_high + 1

            return result

    except (pymysql.err.MySQLError, Exception):
        raise


async def get_progress():
    select_completed = '''SELECT COUNT(*) FROM parts_data
                       WHERE completed_time IS NOT NULL;'''

    select_in_progress = '''SELECT COUNT(*) FROM parts_data
                       WHERE completed_time IS NULL
                       AND issued_time is NOT NULL;'''

    # For url list database
    select_urls_total = '''SELECT COUNT(*) FROM `crawler_parts`'''

    connection = pymysql.connect(host=MYSQL_HOST,
                                 user=MYSQL_USER,
                                 password=MYSQL_PASSWORD,
                                 db=MYSQL_DATABASE,
                                 charset='utf8mb4')

    try:
        with connection.cursor() as cursor:
            cursor.execute(select_urls_total)
            urls_total = cursor.fetchone()

        with psycopg2.connect(**psql_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(select_completed)
                completed = cursor.fetchone()

                cursor.execute(select_in_progress)
                in_progress = cursor.fetchone()

        return {
            'completed': completed[0],
            'in_progress': in_progress[0],
            'urls_total': urls_total[0]
        }

    except (pymysql.err.MySQLError, Exception):
        raise

    finally:
        if connection:
            connection.close()
