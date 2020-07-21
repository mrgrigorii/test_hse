# -*- coding: utf-8 -*-

import argparse
import gzip
import json

PROBLEM_OUTPUT_COLUMNS = [
    'user_id',
    'problem_id',
    'question_id',
    'question',
    'answer',
    'time',
]

VIDEO_OUTPUT_COLUMNS = [
    'user_id',
    'video_id',
    'event_type',
    'time',
]

BASE_VIDEO_EVENTS = [
    'hide_transcript',
    'edx.video.transcript.hidden',
    'load_video',
    'edx.video.loaded',
    'pause_video',
    'edx.video.paused',
    'play_video',
    'edx.video.played',
    'seek_video',
    'edx.video.position.changed',
    'show_transcript',
    'edx.video.transcript.shown',
    'speed_change_video',
    'stop_video',
    'edx.video.stopped',
    'video_hide_cc_menu',
    'video_show_cc_menu',
]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--mode', choices=['problem', 'video'])
    args = parser.parse_args()

    rows_iterator = iterate_rows(args.input)
    output_data = []

    for row in rows_iterator:
        try:
            json_row = parse_row(row)

            if args.mode == 'problem':
                problems = parse_problem_row(json_row)
                output_data += problems
            elif args.mode == 'video':
                video_events = parse_video_row(json_row)
                output_data += video_events
        except Exception as e:
            print(e)

    if args.mode == 'problem':
        columns = PROBLEM_OUTPUT_COLUMNS
    elif args.mode == 'video':
        columns = VIDEO_OUTPUT_COLUMNS
    dump_csv(args.output, output_data, columns)


def iterate_rows(input_gzip):
    with gzip.open(input_gzip, 'rb') as fin:
        row = fin.readline().decode('utf-8')
        while row:
            yield row
            row = fin.readline().decode('utf-8')


def parse_row(row):
    return json.loads(row[row.find('{'):])


def parse_problem_row(row_json):
    user_id = row_json.get('context').get('user_id')
    event_source = row_json.get('event_source')
    if not user_id or event_source != 'server':
        return []

    problems = []
    name = row_json.get('name')
    event_type = row_json.get('event_type')
    if name:
        event_type = name

    if event_type == 'problem_check':
        problem_id = row_json['event']['problem_id']
        time = row_json['time']
        submission = row_json['event']['submission']
        for question_id, value in submission.items():
            question = value['question']
            answer = value['answer']

            if not question:
                question = None
            if not answer:
                answer = None

            problems.append([
                str(user_id),
                str(problem_id),
                str(question_id),
                str(question),
                str(answer),
                str(time),
            ])
    return problems


def parse_video_row(row_json):
    user_id = row_json.get('context').get('user_id')
    if not user_id:
        return []

    event_type = row_json.get('event_type')
    name = row_json.get('name')
    if name:
        event_type = name

    if event_type in BASE_VIDEO_EVENTS:
        video_id = json.loads(row_json.get('event')).get('id')
        time = row_json['time']

        return [[
            str(user_id),
            str(video_id),
            str(event_type),
            str(time),
        ]]
    return []


def dump_csv(output_file, data, columns):
    with open(output_file, 'w', encoding='utf-8') as out:
        out.write('\t'.join(columns))
        out.write('\n')

        data = list(map('\t'.join, data))
        out.write('\n'.join(data))
        out.write('\n')


if __name__ == '__main__':
    main()
