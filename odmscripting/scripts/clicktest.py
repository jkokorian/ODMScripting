# -*- coding: utf-8 -*-
"""
Created on Wed Aug 12 17:14:09 2015

@author: jkokorian
"""

import click

@click.group()
def cli():
    pass

@click.command('list-measurements')
@click.argument('path', type=click.Path(exists=True))
@click.option('--recurse/--no-recurse', default=False, help='search recursively')
def list_measurements(path,recurse=False):
    print path    
    print recurse
    click.echo('Initialized the database')

@click.command()
def dropdb():
    click.echo('Dropped the database')


cli.add_command(list_measurements)
cli.add_command(dropdb)
if __name__ == '__main__':
    cli()