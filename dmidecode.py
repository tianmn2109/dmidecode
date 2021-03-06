__version__ = "0.8.1"


TYPE = {
    0:  'bios',
    1:  'system',
    2:  'base board',
    3:  'chassis',
    4:  'processor',
    7:  'cache',
    8:  'port connector',
    9:  'system slot',
    10: 'on board device',
    11: 'OEM strings',
    #13: 'bios language',
    15: 'system event log',
    16: 'physical memory array',
    17: 'memory device',
    19: 'memory array mapped address',
    24: 'hardware security',
    25: 'system power controls',
    27: 'cooling device',
    32: 'system boot',
    41: 'onboard device',
    }


def parse_dmi(content):
    """
    Parse the whole dmidecode output.
    Returns a list of tuples of (type int, value dict).
    """
    info = []
    lines = iter(content.strip().splitlines())
    while True:
        try:
            line = lines.next()
        except StopIteration:
            break

        if line.startswith('Handle 0x'):
            typ = int(line.split(',', 2)[1].strip()[len('DMI type'):])
            if typ in TYPE:
                info.append((TYPE[typ], _parse_handle_section(lines)))
    return info

def humanize(info):
    def _get(i):
        return [v for j, v in info if j == i]
    d = {}
    system = _get('system')[0]
    d['sn'] = 'SN: %s' % (
    #    system['Manufacturer'],
     #   system['Product Name'],
        system['Serial Number'],
        )
    d['uuid'] = 'UUID: %s ' % (system['UUID'],)

    for cpu in _get('processor'):
        d['cpus'] = '%s %s %s (Core: %s, Thead: %s)' % (
            cpu['Manufacturer'],
            cpu['Family'],
            cpu['Max Speed'],
            cpu['Core Count'],
            cpu['Thread Count'],
            )
    

    cnt, total, unit = 0, 0, None
    slotsnum = 0
    for mem in _get('memory device'):
        if mem['Size'] == 'No Module Installed':
            slotsnum += 1
            continue
        i, unit = mem['Size'].split()
        slotsnum += 1
        cnt += 1
        total += int(i)
    d['memory'] = '%d memory stick(s), %d %s in total' % (
        cnt,
        total,
        unit,
        )
    d['slots'] = '%d memory slot(s)' % (slotsnum)
    return d
#    d = {}
#    item = iter(info)
#    while True:
#        try:
#            each = item.next()
#        except StopIteration:
#            break
    #if d[each[0]] == 'processor':
    
#    return d


def _parse_handle_section(lines):
    """
    Parse a section of dmidecode output

    * 1st line contains address, type and size
    * 2nd line is title
    * line started with one tab is one option and its value
    * line started with two tabs is a member of list
    """
    data = {
        '_title': lines.next().rstrip(),
        }

    for line in lines:
        line = line.rstrip()
        if line.startswith('\t\t'):
            data[k].append(line.lstrip())
        elif line.startswith('\t'):
            k, v = [i.strip() for i in line.lstrip().split(':', 1)]
            if v:
                data[k] = v
            else:
                data[k] = []
        else:
            break

    return data


def profile():
    import os, sys
    if os.isatty(sys.stdin.fileno()):
        content = _get_output()
    else:
        content = sys.stdin.read()

    info = parse_dmi(content)
    _show(info)


def _get_output():
    import subprocess
    output = subprocess.check_output(
        'PATH=$PATH:/bin:/sbin:/usr/bin:/usr/sbin:/usr/local/bin '
        'sudo dmidecode', shell=True)
    return output


def _show(info):
    def _get(i):
        return [v for j, v in info if j == i]

    system = _get('system')[0]
    print '%s %s (SN: %s, UUID: %s)' % (
        system['Manufacturer'],
        system['Product Name'],
        system['Serial Number'],
        system['UUID'],
        )

    for cpu in _get('processor'):
        print '%s %s %s (Core: %s, Thead: %s)' % (
            cpu['Manufacturer'],
            cpu['Family'],
            cpu['Max Speed'],
            cpu['Core Count'],
            cpu['Thread Count'],
            )

    cnt, total, unit = 0, 0, None
    for mem in _get('memory device'):
        if mem['Size'] == 'No Module Installed':
            continue
        i, unit = mem['Size'].split()
        cnt += 1
        total += int(i)
    print '%d memory stick(s), %d %s in total' % (
        cnt,
        total,
        unit,
        )


if __name__ == '__main__':
    profile()
