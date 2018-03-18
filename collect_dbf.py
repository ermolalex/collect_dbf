# -*- coding: utf-8 -*-

import click
from pathlib import Path
from dbf import Table
import sqlite3
import datetime
import os

SHOPS_LIST = ["3", "4"]

def validate_in(ctx, param, value):
    if not value: 
        return value

    _dir = Path(value)
    if not _dir.exists():
        raise click.BadParameter('Указанная папка не существует.')
    if not _dir.is_dir():
        raise click.BadParameter('Указанная папка не существует.')
    return value

def validate_out(ctx, param, value):
    if not value: 
        return value
    db_file = Path(value)
    if not db_file.exists() or not db_file.is_file():
        print('Указанный файл не существует и будет создан новый.')
    return value

def create_conn(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)

    return None

def export_file(conn, dbf_file, shop_number):
    sales_table = []

    str_date = os.path.splitext(str(dbf_file.name))[0] 

    d = Table(str(dbf_file), codepage='cp866')
    d.open()
    for r in d:
        if r.oper == ' 9':
            sales_table.append((shop_number, str_date, r.time.strip(), r.sum ))
    
    conn.executemany("INSERT OR IGNORE INTO sales VALUES(?,?,?,?);", sales_table)
    conn.commit()


###


@click.command()
@click.option('--dbf_dir', callback=validate_in, help='Папка с файлами продаж.', required=True)
@click.option('--sales_db', callback=validate_out, help='Файл базы данных.', required=True)
@click.option('--all', is_flag=True, help='Если указан, обрабатывать все файлы *.dbf в папке. Иначе только за текущую дату')
@click.option('--d', help='Дата в формате [дд-мм-гг].Если указан, обрабатывать только один файл за указанную дату')
@click.option('--shop', type=click.Choice(SHOPS_LIST), help='Номер магазина.', required=True)


def transform(shop, dbf_dir, sales_db, all, d):
    click.echo('Обрабатываем магазин %s в папке %s' % (shop, dbf_dir))

    conn = create_conn(sales_db)
    create_table_sql = """
        CREATE TABLE IF NOT EXISTS sales (
            shop integer,
            date char(8),     
            time char(8),
            sum real,
            CONSTRAINT sale_unique UNIQUE (shop, date, time)
        ); """

    conn.execute(create_table_sql)

    if all:
        dbfs = Path(dbf_dir)
        for f in dbfs.glob('*.dbf'):
            export_file(conn, f, shop)
    else:
        if d:
            f_name = d + ".dbf"
        else:
            now = datetime.datetime.now()
            f_name = now.strftime("%d-%m-%y") + ".dbf"
        f = Path(dbf_dir) / f_name
        if not f.exists():
            print("Файл %s не существует" % f)
            return
        export_file(conn, f, shop)

    conn.close()

if __name__ == '__main__':
    transform()