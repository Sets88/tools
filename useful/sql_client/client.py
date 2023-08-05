import os
from time import time
import asyncio

import kaa
from kaa.cui.main import run
from kaa.cui.editor import TextEditorWindow
from kaa.addon import command
from kaa.addon import setup
from kaa.addon import alt
from kaa.addon import ctrl
from kaa.addon import backspace
import visidata
import curses
from ssh_crypt import E

HOST = None
USERNAME = None
PASSWORD = None
PORT = None
ENGINE = None
DBNAME = None


async def execute_clickhouse(sql: str, connection_data: dict) -> list[dict]:
    # imported here to make this dependency optional
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


async def execute_mysql(sql: str, connection_data: dict) -> list[dict]:
    # imported here to make this dependency optional
    import aiomysql

    conn = await aiomysql.connect(
        host=connection_data['host'],
        port=int(connection_data.get('port', 3306) or 3306),
        user=connection_data['username'],
        password=connection_data['password'],
        db=connection_data.get('dbname', ''),
    )

    async with conn.cursor(aiomysql.DictCursor) as cur:
        await cur.execute(sql)
        return await cur.fetchall()


async def execute_postgres(sql: str, connection_data: dict) -> list[dict] | None:
    # imported here to make this dependency optional
    import aiopg
    import psycopg2

    if sql.strip().startswith('\\c '):
        global DBNAME
        DBNAME = sql.strip().split(' ')[1]
        return

    if sql.strip().startswith('\\d '):
        sql = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{sql.strip().split(' ')[1]}'"
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


async def execute(sql: str, connection_data: dict) -> list[dict] | None:
    engine = connection_data.pop('engine')
    if engine == 'clickhouse':
        return await execute_clickhouse(sql, connection_data)
    if engine == 'mysql':
        return await execute_mysql(sql, connection_data)
    if engine == 'postgres':
        return await execute_postgres(sql, connection_data)


def get_sel(wnd: TextEditorWindow) -> str:
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


def get_cur_line(wnd: TextEditorWindow) -> str | None:
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


async def await_and_print_time(wnd: TextEditorWindow, coro: asyncio.coroutines) -> list[dict] | None:
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


@command('run.query')
def run_query(wnd: TextEditorWindow):
    sel = get_sel(wnd)

    if not sel:
        sel = get_cur_line(wnd)

    selection = sel.strip()

    print(wnd)
    import time; time.sleep(5)

    try:
        data = asyncio.run(await_and_print_time(
            wnd,
            execute(selection, dict(
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
def editor(mode):

    # register command to the mode
    mode.add_command(run_query)

    # add key bind th execute 'run.query'
    mode.add_keybinds(keys={
        (alt, 'r'): 'run.query',
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
