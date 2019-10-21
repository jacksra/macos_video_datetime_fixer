import datetime as dt
import os
import shutil
import subprocess


def call(args, func=subprocess.check_call, logfile=None):
    print '  ' + ' '.join(args)

    kwargs = {}
    if logfile:
        kwargs['stdout'] = logfile
        kwargs['stderr'] = subprocess.STDOUT

    return func(args, **kwargs)


def list_video_filenames():
    dirents = os.listdir('.')

    filenames = [f for f in dirents if os.path.isfile(f)]

    extensions = ('.mov', '.mpg', '.mp4', '.avi')

    return [
        f for f in filenames
        if any([f.lower().endswith(e) for e in extensions])
    ]


def replace_extension(filename, extension):
    return '.'.join(
        filename.split('.')[:-1] + [extension],
    )


def extract_file_modify_date(filename, logfile):
    exifout = call(
        [
            'exiftool',
            '-a',
            '-s',
            '-time:FileModifyDate',
            filename,
        ],
        func=subprocess.check_output,
    ).strip()

    logfile.write(exifout)

    return exifout.split(': ')[-1].strip()


def convert_to_mp4(filename, target_path, logfile):
    call(
        [
            '/Applications/HandBrakeCLI',
            '-e', 'x264',
            '--encoder-preset', 'fast',
            '-i', filename,
            '-o', target_path,
        ],
        logfile=logfile,
    )


def insert_datetime_original(filename, datetime, logfile):
    call(
        [
            'exiftool',
            '-datetimeoriginal=%s' % datetime,
            filename,
        ],
        logfile=logfile,
    )

    call(
        [
            'exiftool',
            '-delete_original!',
            filename,
        ],
        logfile=logfile,
    )


def v2():
    outputdirname = 'output'
    if not os.path.exists(outputdirname):
        os.mkdir(outputdirname)

    logsdirname = 'logs'
    logsdirpath = os.path.join(outputdirname, logsdirname)
    if not os.path.exists(logsdirpath):
        os.mkdir(logsdirpath)

    filenames = list_video_filenames()

    for filename in filenames:
        print filename

        target_filename = filename
        convert = False
        if filename.lower().endswith('.mpg') or filename.lower().endswith('.avi'):
            target_filename = replace_extension(filename, 'MP4')
            convert = True

        target_path = os.path.join(outputdirname, target_filename)
        if os.path.exists(target_path):
            print '  %s exists, skipping' % target_path
            continue

        logfile = open(
            os.path.join(
                logsdirpath,
                target_filename + '.txt'
            ),
            'w',
        )

        if convert:
            convert_to_mp4(filename, target_path, logfile)
        else:
            call(['cp', filename, target_path], logfile=logfile)

        file_mod_datetime = extract_file_modify_date(filename, logfile)

        insert_datetime_original(target_path, file_mod_datetime, logfile)


v2()


def v1():
    dirents = os.listdir('.')
    mp4_files = [d for d in dirents if d.endswith('.mp4')]
    for mp4_file in mp4_files:
        datetimestr, file_with_numeric_suffix = mp4_file.split('__')
        file_without_extension = file_with_numeric_suffix.split(' ')[0]
        filename = file_without_extension + '.mp4'
        #datetimestr = datetimestr.replace('-', ':').replace('_', ' ')
        datetime = dt.datetime.strptime(datetimestr, '%Y-%m-%d_%I:%M %p')
        print datetime.strftime('%Y:%m:%d %H:%M:%S')

        subprocess.check_call(
            [
                'exiftool',
                '-datetimeoriginal=%s' % datetime,
                mp4_file,
            ],
        )

        subprocess.check_call(
            [
                'mv',
                mp4_file,
                filename,
            ],
        )
