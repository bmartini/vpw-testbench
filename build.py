#!/usr/bin/env python3


import vpw.util as vpw
import click


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option('-c', '--clock', default='clk', help='Clock name of top module.')
@click.option('-n', '--name', default='example', help='Name of top module.')
def main(name: str, clock: str):

    vpw.parse(name = name, clock = clock)


if __name__ == '__main__':
    main()
