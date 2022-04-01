#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import configparser


def run_query(cmd, query, dbname, query_timeout=20):
    total_cmd = cmd + query
    result = subprocess.run(total_cmd, shell=True, stdout=subprocess.PIPE, timeout=query_timeout)
    if result.stderr:
        print(result.stderr.decode('utf-8'))
    return result.stdout.decode('utf-8')


def parse_config_file():
    MK_CONFDIR = os.getenv("MK_CONFDIR") or "/etc/check_mk"
    config_file = MK_CONFDIR + "/maxdb.cfg"
    config = configparser.ConfigParser()
    config.read(config_file)
    if not config:
        print("<<<Check_MK>>>")
        print("Missing Config file for MaxDB Plugin")
        sys.exit(2)
    sections_dict = {}
    sections = config.sections()
    for section in sections:
        options = config.options(section)
        temp_dict = {}
        for option in options:
            temp_dict[option] = config.get(section, option)
        sections_dict[section] = temp_dict
    return sections_dict


def main():
    config = parse_config_file()
    known_querys = {
        'state': ['db_state'],
        'backup:sep(124)': ['backup_history_list -c LABEL,ACTION,START,STOP,RC,ERROR -I'],
        'data:sep(61)': [
            "sql_executenice SELECT A.USEDSIZE,A.USABLESIZE,S.USED_LOG_PAGES*D.PAGESIZE_IN_KB,"
            "S.USED_LOG_PAGES,D.ACTIVE_SESSIONS,D.DATACACHE_HITRATE,S.LOG_PAGES*D.PAGESIZE_IN_KB,"
            "S.LOG_PAGES,S.LOG_NOT_SAVED,D.MAXUSERS,D.DATABASEFULL,D.AUTOSAVESTANDBY,D.BADINDEXES,"
            "D.LOGFULL,D.BADVOLUMES FROM SYSDD.DATASTATISTICS A,SYSDD.SERVERDB_STATS S,SYSDD.DBM_STATE D"
        ],
    }
    for key, value in config.items():
        run_checks = eval(value.get('modules', "['state']"))
        cmd_line = value.get('cmd_tool', f'/sapdb/{key}/db/bin/dbmcli')
        cmd_line += f" -d {key} -u {value.get('user')},{value.get('password')} "
        for check, queries in known_querys.items():
            if check in run_checks:
                print(f"<<<maxdb_{check}>>>")
                print(f"[[{key}]]")
                for query in queries:
                    print(
                        run_query(cmd=cmd_line,
                                  query=query,
                                  dbname=key,
                                  query_timeout=int(value.get('timeout', '20'))))
                if check == 'state':
                    print(
                        run_query(cmd="/sapdb/programs/bin/sdbregview -l",
                                  query="",
                                  dbname=key,
                                  query_timeout=int(value.get('timeout', '20'))))


if __name__ == "__main__":
    main()
