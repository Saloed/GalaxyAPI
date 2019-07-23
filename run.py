#!/usr/bin/python
import os

from argparse import ArgumentParser

try:
    import ConfigParser as configparser
except ImportError:
    import configparser

parser = ArgumentParser()
parser.add_argument('config', type=str, help='API configuration file')


def get_port(config):
    port = 80 if 'SSL' not in config.sections() else 443
    return '-p 8000:%d' % port


def get_name(config):
    return '--name galaxy-api'


def get_image(config):
    return 'galaxy-api'


def get_additional_flags(config):
    return '-it --rm'


def get_config_file_mapping(config_path):
    return get_file_mapping(config_path, '/etc/galaxy/config')


def get_log_file_mapping(config):
    if 'LOG' not in config.sections():
        return ''
    log_dir = config.get('LOG', 'DIR')
    logs = {
        'api': '/var/log/galaxy-api',
        'nginx': '/var/log/nginx',
        'supervisor': '/var/log/supervisor',
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
    if 'SSL' not in config.sections():
        return ''

    pem_file = config.get('SSL', 'PEM')
    key_file = config.get('SSL', 'KEY')

    return combine(
        get_environment('NGINX_ENABLE_SSL', 'True'),
        get_file_mapping(pem_file, '/etc/nginx/certs/ssl-cert.pem'),
        get_file_mapping(key_file, '/etc/nginx/certs/ssl-cert.key')
    )


def get_environment(key, value):
    return '-e %s=%s' % (key, value)


def get_file_mapping(from_file, to_file):
    abs_from_path = os.path.abspath(from_file)
    return '-v %s:%s' % (abs_from_path, to_file)


def combine(*items):
    return ' '.join(items)


def run(rel_config_path):
    config = configparser.ConfigParser()
    config.read(rel_config_path)

    command = combine(
        'docker run',
        get_port(config),
        get_name(config),
        get_config_file_mapping(rel_config_path),
        get_log_file_mapping(config),
        get_ssl_config(config),
        get_additional_flags(config),
        get_image(config)
    )
    os.system(command)


if __name__ == '__main__':
    args = parser.parse_args()
    run(args.config)
