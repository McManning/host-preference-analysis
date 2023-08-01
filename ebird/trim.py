
# Run through the subset of ebird data and trim it down to only data we want
# to import into Postgres. We want *all* birds observed, location, and dates.
import csv
import pandas


sources = [
    {
        'name': 'Spring 2021 eBird data',
    },
    {
        'name': 'Summer 2021 eBird data',
    },
    {
        'name': 'Fall 2021 eBird data',
    },
    {
        'name': 'Spring 2022 eBird data',
    }
]


def process():
    with open('trimmed.csv', 'w', newline='', encoding='utf8') as fout:
        writer = csv.writer(fout)
        writer.writerow(['global_unique_identifier', 'common_name', 'scientific_name',
                        'observation_count', 'county', 'latitude', 'longitude', 'observation_date'])

        x_omitted = 0

        for source in sources:
            print(source['name'])
            # df = pandas.read_csv(source['name'] + '.csv', delimiter='\t')
            # print(df)

            with open(source['name'] + '.csv', 'r', encoding='utf8') as f:
                reader = csv.DictReader(f, delimiter='\t')

                count = 0
                for line in reader:
                    # print(
                    #     f"guid: {line['GLOBAL UNIQUE IDENTIFIER']} cname: {line['COMMON NAME']}")

                    # Some observations use 'X' as the count and an attached spreadsheet.
                    # We don't have this attachment data in the export from eBird, so it's omitted.
                    if line['OBSERVATION COUNT'] == 'X':
                        x_omitted += 1
                        continue

                    # Pandas would be faster, honestly.
                    writer.writerow([
                        line['GLOBAL UNIQUE IDENTIFIER'],
                        line['COMMON NAME'],
                        line['SCIENTIFIC NAME'],
                        line['OBSERVATION COUNT'],
                        line['COUNTY'],
                        line['LATITUDE'],
                        line['LONGITUDE'],
                        line['OBSERVATION DATE'],
                    ])

                    count += 1
                    # if count == 10:
                    #     break
                    if count % 10000 == 0:
                        print(count)

        print(f'Omitted a total of {x_omitted} X rows')


if __name__ == '__main__':
    process()
