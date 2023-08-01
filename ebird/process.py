"""
Process the raw eBird data dump and extract out subsets
into separate files based on collection seasons.
"""
from datetime import datetime

SRC = './imports/ebd_US-OH_relApr-2023.txt'

outputs = [
    # Start/end dates are inclusive
    {
        'name': 'Spring 2021 eBird data',
        'start': '2021-05-21',
        'end': '2021-06-14'
    },
    {
        'name': 'Summer 2021 eBird data',
        'start': '2021-06-21',
        'end': '2021-09-20',
    },
    {
        'name': 'Fall 2021 eBird data',
        'start': '2021-10-04',
        'end': '2021-11-04',
    },
    {
        'name': 'Spring 2022 eBird data',
        'start': '2022-03-25',
        'end': '2022-05-12',
    }
]


def process():
    batch_size = 1_000_000

    # Batch open handles and transform dates
    for output in outputs:
        output['handle'] = open(
            'csv/{}.csv'.format(output['name']), 'w', encoding='utf8')
        output['buffer'] = []
        output['start'] = datetime.strptime(output['start'], '%Y-%m-%d')
        output['end'] = datetime.strptime(output['end'], '%Y-%m-%d')

    # Scan our giant file
    line_count = 0

    with open(SRC, 'r', encoding='utf8') as f:
        for line in f:
            # Replicate CSV header to all output files
            if line_count == 0:
                for output in outputs:
                    output['handle'].write(line)
            else:
                # Extract observation date (column 30) and find a bucket
                columns = line.split('\t')
                date = datetime.strptime(columns[30], '%Y-%m-%d')

                # I'm not assuming this data is sorted by observation date, so I need to check all buckets
                for output in outputs:
                    if date >= output['start'] and date <= output['end']:
                        output['buffer'].append(line)

                        # Buffered write op, cuz I/O
                        if len(output['buffer']) == batch_size:
                            output['handle'].writelines(output['buffer'])
                            output['buffer'] = []

                # Periodic status updates so we know we didn't just hang
                if line_count % batch_size == 0:
                    print('On line {} with date {}'.format(line_count, date))

            line_count += 1

    # Flush buffers and close handles
    for output in outputs:
        if len(output['buffer']) > 0:
            output['handle'].writelines(output['buffer'])

        output['handle'].close()


if __name__ == '__main__':
    process()
