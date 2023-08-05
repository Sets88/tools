import os
import sys
from time import time
from time import sleep
import asyncio
from concurrent.futures import ProcessPoolExecutor

import kaa
from kaa.cui.main import run
from kaa.addon import command, setup, alt, ctrl, backspace
import visidata
import curses
from ssh_crypt import E


HOST = None
USERNAME = None
PASSWORD = None
PORT = None
ENGINE = None
DBNAME = None


CONNECTION = None



async def execute_clickhouse(sql: str, connection_data: dict):
    import asynch

    conn = await asynch.connect(
        host=connection_data['host'],
        port=int(connection_data.get('port', 9000) or 9000),
        database=connection_data.get('dbname', 'default') or 'default',
        user=connection_data['username'],
        password = connection_data['password'],
    )

    async with conn.cursor(cursor=asynch.cursors.DictCursor) as cursor:
        await cursor.execute(sql)
        return await cursor.fetchall()


async def execute_mysql(sql, connection_data):
    import aiomysql

    conn = await aiomysql.connect(
        host=connection_data['host'],
        port=int(connection_data.get('port', '3306') or 3306),
        user=connection_data['username'],
        password=connection_data['password'],
        db=connection_data.get('dbname', ''),
    )

    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(sql)
        return await cur.fetchall()


async def execute_postgres(sql, connection_data):
    import aiopg
    import psycopg2

    if sql.strip().startswith('\\c '):
        global DBNAME
        DBNAME = sql.strip().split(' ')[1]
        return

    if sql.strip().startswith('\\dt'):
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"

    if sql.strip().startswith('\\d '):
        sql = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{}'".format(
            sql.strip().split(' ')[1])
    if sql.strip() == ('\\d'):
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' AND table_type='BASE TABLE';"
    if sql.strip().startswith('\\l'):
        sql = "SELECT datname FROM pg_database;"

    conn = await aiopg.connect(
        host=connection_data['host'],
        port=int(connection_data.get('port', '5432') or 5432),
        user=connection_data['username'],
        password=connection_data['password'],
        dbname=connection_data.get('dbname', ''),
    )

    try:
        async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            await cur.execute(sql)
            return await cur.fetchall()
    finally:
        conn.close()


def execute(sql: str, connection_data: dict):
    engine = connection_data.pop('engine')
    if engine == 'clickhouse':
        return execute_clickhouse(sql, connection_data)
    if engine == 'mysql':
        return execute_mysql(sql, connection_data)
    if engine == 'postgres':
        return execute_postgres(sql, connection_data)


async def aexecute(sql: str, connection_data: dict):
    engine = connection_data.pop('engine')
    if engine == 'clickhouse':
        return await execute_clickhouse(sql, connection_data)
    if engine == 'mysql':
        return await execute_mysql(sql, connection_data)
    if engine == 'postgres':
        return await execute_postgres(sql, connection_data)


def get_sel(wnd):
    if wnd.screen.selection.is_selected():
        if not wnd.screen.selection.is_rectangular():
            f, t = wnd.screen.selection.get_selrange()
            return wnd.document.gettext(f, t)
        else:
            s = []
            (posfrom, posto, colfrom, colto
             ) = wnd.screen.selection.get_rect_range()

            while posfrom < posto:
                sel = wnd.screen.selection.get_col_string(
                    posfrom, colfrom, colto)
                if sel:
                    f, t, org = sel
                    s.append(org.rstrip('\n'))
                else:
                    s.append('')
                posfrom = wnd.document.geteol(posfrom)

            return '\n'.join(s)


def get_cur_line(wnd):
    pos = wnd.cursor.pos
    tol = wnd.cursor.adjust_nextpos(
        wnd.cursor.pos,
        wnd.document.gettol(wnd.cursor.pos))
    eol = wnd.cursor.adjust_nextpos(
        wnd.cursor.pos,
        wnd.document.geteol(tol))

    eol, sel = wnd.screen.document.getline(tol)

    if sel:
        return sel


async def await_and_print_time(wnd, coro):
    start = time()
    task = asyncio.create_task(coro)

    while not task.done():
        wnd.mainframe._cwnd.timeout(0)
        key = wnd.mainframe._cwnd.getch()

        if key == 27:
            task.cancel()
            return

        await asyncio.sleep(0.1)

        print(f'Running (press ESC to cancel): {round(time() - start, 2)}s ')
        print('\033[F', end='')

    return await task


@command('run.clickhouse')
def testcommand(wnd):
    sel = get_sel(wnd);
    if not sel:
        sel = get_cur_line(wnd)

    selection = sel.strip()

    try:
        data = asyncio.run(await_and_print_time(
            wnd,
            aexecute(selection, dict(
                host=HOST, username=USERNAME, password=PASSWORD, port=PORT, engine=ENGINE, dbname=DBNAME
            )))
        )
        visidata.vd.run()

        if not data:
            kaa.app.messagebar.set_message('No rows returned')
            return

        visidata.vd.view(data)
    except Exception as exc:
        kaa.app.messagebar.set_message(str(exc))
    finally:
        curses.endwin()
        curses.curs_set(1)
        wnd.draw_screen(force=True)


@setup('kaa.filetype.default.defaultmode.DefaultMode')
def command_sample(mode):

    # register command to the mode
    mode.add_command(testcommand)

    # add key bind th execute 'run.clickhouse'
    mode.add_keybinds(keys={
        (alt, 'r'): 'run.clickhouse',
        (ctrl, 's'): 'file.save',
        (ctrl, 'q'): 'file.quit',
        (alt, backspace): 'edit.backspace.word'
    })


if __name__ == '__main__':
    HOST = os.environ['CLHOST']
    USERNAME = os.environ['CLUSER']
    PASSWORD = str(E(os.environ['CLPASS']))
    PORT = os.environ.get('CLPORT')
    DBNAME = os.environ.get('CLDBNAME')
    ENGINE = os.environ.get('CLENGINE')
    run()
