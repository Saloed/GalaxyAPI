#!/usr/bin/python
import os

from argparse import ArgumentParser

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

parser = ArgumentParser()
parser.add_argument('config', type=str, help='API configuration file')
parser.add_argument('--debug', action='store_true', help='Runs container with shell')


def get_port(config):
    port = 80 if not config.has_section('SSL') else 443
    host_port = 8000 if not config.has_option('API', 'PORT') else config.getint('API', 'PORT')
    return '-p %d:%d' % (host_port, port)


def get_name(config):
    return '--name galaxy-api'


def get_image(config):
    return 'conyashka/galaxy-api:latest'


def get_additional_flags(config):
    if config.debug:
        return combine('--rm', '-it')
    return combine('--rm', '-d')


def get_config_file_mapping(config_path):
    return get_file_mapping(config_path, '/etc/galaxy/config')


def get_log_file_mapping(config):
    if not config.has_section('LOG'):
        return ''
    log_dir = config.get('LOG', 'DIR')
    logs = {
        'api': '/var/log/galaxy-api',
        'nginx': '/var/log/nginx',
        'supervisor': '/var/log/supervisor',
        'redis': '/var/log/redis'
    }
    log_mappings = []
    for name, path in logs.items():
        local_path = os.path.join(log_dir, name)
        try:
            os.makedirs(local_path)
        except OSError:
            if not os.path.isdir(local_path):
                raise
        mapping = get_file_mapping(local_path, path)
        log_mappings.append(mapping)

    return combine(*log_mappings)


def get_ssl_config(config):
    if not config.has_section('SSL'):
        return ''

    cert_file = config.get('SSL', 'CERT')
    key_file = config.get('SSL', 'KEY')
    password_file = config.get('SSL', 'PASSWORD')

    return combine(
        get_environment('NGINX_ENABLE_SSL', 'True'),
        get_file_mapping(cert_file, '/etc/nginx/certs/ssl-cert.pem'),
        get_file_mapping(key_file, '/etc/nginx/certs/ssl-cert.key'),
        get_file_mapping(password_file, '/etc/nginx/certs/ssl-cert.pass')
    )


def get_environment(key, value):
    return '-e %s=%s' % (key, value)


def get_file_mapping(from_file, to_file):
    abs_from_path = os.path.abspath(from_file)
    return '-v %s:%s' % (abs_from_path, to_file)


def combine(*items):
    return ' '.join(items)


def get_descriptions(config):
    if not config.has_option('API', 'DESCRIPTIONS'):
        raise ValueError('Descriptions path is required')
    descriptions = config.get('API', 'DESCRIPTIONS')
    return combine(
        get_file_mapping(descriptions, '/var/galaxy/descriptions'),
        get_environment('GALAXY_DESCRIPTIONS', '/var/galaxy/descriptions')
    )


def get_debug_entrypoint(config):
    if not config.debug:
        return ''
    return '--entrypoint /bin/bash'

def run(args):
    rel_config_path = args.config
    config = configparser.ConfigParser()
    if not config.read(rel_config_path):
        raise ValueError('Config file not specified')

    command = combine(
        'docker run',
        get_port(config),
        get_name(config),
        get_config_file_mapping(rel_config_path),
        get_descriptions(config),
        get_log_file_mapping(config),
        get_ssl_config(config),
        get_debug_entrypoint(args),
        get_additional_flags(args),
        get_image(config)
    )
    os.system(command)


if __name__ == '__main__':
    parsed_args = parser.parse_args()
    run(parsed_args)
