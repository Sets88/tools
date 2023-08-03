import os
import sys
from time import time
import asyncio

import kaa
from kaa.cui.main import run
from kaa.addon import command, setup, alt, ctrl, backspace
import visidata
import curses
from ssh_crypt import E
import clickhouse_connect


client = clickhouse_connect.get_client(
    host=os.environ['CHHOST'],
    username=os.environ['CHUSER'],
    password=str(E(os.environ['CHPASS'])),
    port=os.environ.get('CHPORT', 8123)
)


def execute(sql):
    result = client.query(sql, column_oriented=True)
    data = result.result_rows
    res = [{result.column_names[i]: cell for i, cell in enumerate(x)} for x in data]
    return res


async def aexecute(sql):
    return await asyncio.to_thread(execute, sql)


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


async def await_and_print_time(coro):
    start = time()
    task = asyncio.create_task(coro)
    while not task.done():
        await asyncio.sleep(0.1)
        print(f'Running: {round(time() - start, 2)}')
        print('\033[F', end='')

    return await task


@command('run.clickhouse')
def testcommand(wnd):
    sel = get_sel(wnd);
    if not sel:
        sel = get_cur_line(wnd)

    selection = sel.strip()

    try:
        visidata.vd.run()
        data = asyncio.run(await_and_print_time(aexecute(selection)))

        if not data:
            kaa.app.messagebar.set_message('No rows returned')
            return

        visidata.vd.view(data)
    finally:
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


run()
