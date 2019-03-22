import os
import sys
import asyncio
import logging
import psycopg2
import pymysql.cursors
from datetime import datetime, timedelta


num_of_urls = os.environ.get('NUM_OF_URLS', 300)
url_num_low = 1

MYSQL_DATABASE = os.environ.get('MYSQL_DATABASE')
MYSQL_HOST = os.environ.get('MYSQL_HOST')
MYSQL_PORT = int(os.environ.get('MYSQL_PORT'))
MYSQL_USER = os.environ.get('MYSQL_USER')
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')

psql_info = {
    'user': os.environ.get('POSTGRES_USER'),
    'password': os.environ.get('POSTGRES_PASSWORD'),
    'host': os.environ.get('POSTGRES_HOST'),
    'port': os.environ.get('POSTGRES_PORT'),
    'database': os.environ.get('POSTGRES_DB')
}


async def get_url_list():
    global url_num_low
    url_num_high = url_num_low + int(num_of_urls) - 1

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
    connection = pymysql.connect(host=MYSQL_HOST,
                                 user=MYSQL_USER,
                                 password=MYSQL_PASSWORD,
                                 db=MYSQL_DATABASE,
                                 charset='utf8mb4')

    # For url list database
    select_urls_total = '''SELECT COUNT(*) FROM `crawler_parts`'''

    # The rest are for postgres
    select_completed = '''SELECT COUNT(*) FROM parts_data
                       WHERE completed_time IS NOT NULL;'''

    select_in_progress = '''SELECT COUNT(*) FROM parts_data
                       WHERE completed_time IS NULL
                       AND issued_time is NOT NULL;'''

    select_days = '''SELECT COUNT(*) FROM parts_data
                  WHERE completed_time BETWEEN %s and %s'''

    today = datetime.now().date()
    day_two = today - timedelta(days=1)
    day_three = today - timedelta(days=2)
    day_four = today - timedelta(days=3)
    start = '00:00:00.000000'
    end = '23:59:59.999999'

    try:
        with connection.cursor() as cursor:
            cursor.execute(select_urls_total)
            urls_total = cursor.fetchone()[0]

        with psycopg2.connect(**psql_info) as conn:
            with conn.cursor() as cursor:
                cursor.execute(select_completed)
                completed_total = cursor.fetchone()[0]

                cursor.execute(select_in_progress)
                in_progress = cursor.fetchone()[0]

                cursor.execute(
                    select_days,
                    [f'{today} {start}', f'{today} {end}']
                )
                today_complete = cursor.fetchone()[0]

                cursor.execute(
                    select_days,
                    [f'{day_two} {start}', f'{day_two} {end}']
                )
                day_two_complete = cursor.fetchone()[0]

                cursor.execute(
                    select_days,
                    [f'{day_three} {start}', f'{day_three} {end}']
                )
                day_three_complete = cursor.fetchone()[0]

                cursor.execute(
                    select_days,
                    [f'{day_four} {start}', f'{day_four} {end}']
                )
                day_four_complete = cursor.fetchone()[0]

        # Using the f-strings {:,} to put a comma every 1000s
        return {
            'completed_total': f'{completed_total:,}',
            'in_progress': f'{in_progress:,}',
            'urls_total': f'{urls_total:,}',
            'total_left': f'{(urls_total - completed_total):,}',
            'today_complete': f'{today_complete:,}',
            'day_two_complete': f'{day_two_complete:,}',
            'day_three_complete': f'{day_three_complete:,}',
            'day_four_complete': f'{day_four_complete:,}'
        }

    except (pymysql.err.MySQLError, Exception):
        raise

    finally:
        if connection:
            connection.close()
