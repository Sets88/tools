import os
from time import time
import asyncio
from functools import partial

import kaa
from kaa.cui.main import run
from kaa.cui.editor import TextEditorWindow
from kaa.filetype.default import defaultmode
from kaa.addon import command
from kaa.addon import setup
from kaa.addon import alt
from kaa.addon import ctrl
from kaa.addon import backspace
from kaa.theme import Style
from kaa.syntax_highlight import Span, SingleToken, Tokenizer, Keywords, Token
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
    from aiohttp import ClientSession
    import aiochclient
    global DBNAME
    db = connection_data.get('dbname', 'default') or 'default'

    if sql.strip().upper().startswith('USE '):
        db = sql.strip().split(' ')[1].rstrip(';')

    async with ClientSession() as sess:
        port = connection_data.get('port', '8123') or '8123'

        client = aiochclient.ChClient(
            sess,
            url=f"http://{connection_data['host']}:{port}",
            database=db,
            user=connection_data['username'],
            password = connection_data['password'],
        )

        data = [dict(x) for x in await client.fetch(sql)]

        if DBNAME != db:
            DBNAME = db

        return (data, '')


async def execute_mysql(sql: str, connection_data: dict) -> list[dict]:
    # imported here to make this dependency optional
    import aiomysql
    global DBNAME

    db = connection_data.get('dbname', '')

    if sql.strip().upper().startswith('USE '):
        db = sql.strip().split(' ')[1].rstrip(';')

    conn = await aiomysql.connect(
        host=connection_data['host'],
        port=int(connection_data.get('port', 3306) or 3306),
        user=connection_data['username'],
        password=connection_data['password'],
        db=db,
        autocommit=True
    )

    if DBNAME != db:
        DBNAME = db

    try:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql)
            data = await cur.fetchall()

            if not data and cur.rowcount:
                return (data, f'{cur.rowcount} rows affected')

            return (data, f'{cur.rowcount} rows returned')
    finally:
        conn.close()


async def execute_postgres(sql: str, connection_data: dict) -> list[dict] | None:
    # imported here to make this dependency optional
    import aiopg
    import psycopg2
    global DBNAME

    db = connection_data.get('dbname', '')

    if sql.strip().startswith('\\c '):
        db = sql.strip().split(' ')[1].rstrip(';')
        sql = ''

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
        dbname=db,
    )

    if DBNAME != db:
        DBNAME = db

    try:
        async with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            await cur.execute(sql)
            rowcount = cur.rowcount
            try:
                data = await cur.fetchall()
            except psycopg2.ProgrammingError:
                return ([], f'{rowcount} rows affected')

            return (data, f'{rowcount} rows returned')
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
        pos,
        wnd.document.gettol(pos))

    _, sel = wnd.screen.document.getline(tol)

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


def fix_visidata_curses():
    if visidata.color.colors.color_pairs:
        for (fg, bg), (pairnum, _) in visidata.color.colors.color_pairs.items():
            curses.init_pair(pairnum, fg, bg)


def fix_kaa_curses(wnd):
    curses.endwin()
    kaa.app.show_cursor(1)

    for pairnum, (fg, bg) in enumerate(kaa.app.colors.pairs.keys()):
        curses.init_pair(pairnum, fg, bg)

    wnd.draw_screen(force=True)


@command('run.query')
def run_query(wnd: TextEditorWindow):
    sel = get_sel(wnd)

    if not sel:
        sel = get_cur_line(wnd)

    selection = sel.strip()
    start = time()
    end = None
    message = ''

    try:
        data = asyncio.run(await_and_print_time(
            wnd,
            execute(selection, dict(
                host=HOST, username=USERNAME, password=PASSWORD, port=PORT, engine=ENGINE, dbname=DBNAME
            )))
        )

        end = time()

        if not data:
            message = 'No rows returned'
            return

        rows, message = data

        fix_visidata_curses()
        visidata.vd.options.set('disp_float_fmt', '')
        visidata.vd.run()
        visidata.vd.view(rows)
    except Exception as exc:
        end = time()
        message = str(exc)
    finally:
        wnd.document.set_title(f"{ENGINE} {HOST} {DBNAME}")
        kaa.app.messagebar.set_message(f'{round(end - start, 2)}s {message}')
        fix_kaa_curses(wnd)


def on_keypressed(self, wnd, event, s, commands, candidate):
    wnd.document.set_title(f"{ENGINE} {HOST} {DBNAME}")
    return self._on_keypressed(wnd, event, s, commands, candidate)


## Syntax highlight ##

sql_editor_themes = {
    'basic': [
        Style('string', 'Green', None, bold=True),
        Style('number', 'Yellow', None, bold=True),
    ]
}


KEYWORDS = [
    'SELECT', 'UPDATE', 'DELETE', 'DROP', 'ALTER', 'COLUMN', 'USE',
    'FROM', 'JOIN', 'OUTER', 'INNER', 'LIMIT', 'ORDER BY', 'AS',
    'SHOW', 'FROM', 'WHERE', 'DESC', 'TABLES', 'CREATE', 'TABLE',
    'SET', 'IS', 'NOT', 'NULL', 'ON', 'IN', 'LIKE', 'ILIKE', 'AND',
    'OR', 'INSERT', 'INTO', 'VALUES', 'INTERVAL', 'GROUP', 'BY',
    'HAVING', 'GRANT'
]


def sqleditor_tokens() -> list[tuple[str, Token]]:
    return [
        ('comment1', Span('comment', r'--', '$')),
        ('comment2', Span('comment', r'\#', '$')),
        ("string1", Span('string', '"', '"', escape='\\')),
        ("string2", Span('string', "'", "'", escape='\\')),
        ("number", SingleToken('number', [r'\b[0-9]+(\.[0-9]*)*\b', r'\b\.[0-9]+\b'])),
        ("keyword", Keywords('keyword', KEYWORDS)),
    ]


def make_tokenizer() -> Tokenizer:
    return Tokenizer(tokens=sqleditor_tokens())

# -----------

@setup('kaa.filetype.default.defaultmode.DefaultMode')
def editor(mode):
    # register command to the mode
    mode.add_command(run_query)
    mode._on_keypressed = mode.on_keypressed
    mode.on_keypressed = partial(on_keypressed, mode)

    # add key bind th execute 'run.query'
    mode.add_keybinds(keys={
        (alt, 'r'): 'run.query',
        (ctrl, 's'): 'file.save',
        (ctrl, 'q'): 'file.quit',
        (alt, backspace): 'edit.backspace.word'
    })

    # Syntax highlight
    mode.tokenizer = make_tokenizer()
    mode.themes.append(sql_editor_themes)


if __name__ == '__main__':
    defaultmode.DefaultMode.SHOW_LINENO = True
    HOST = os.environ['CLHOST']
    USERNAME = os.environ['CLUSER']
    PASSWORD = str(E(os.environ['CLPASS']))
    PORT = os.environ.get('CLPORT')
    DBNAME = os.environ.get('CLDBNAME')
    ENGINE = os.environ.get('CLENGINE')
    run()
