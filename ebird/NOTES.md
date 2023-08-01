The full eBird export `ebd_US-OH_relApr-2023` was split into seasonal `.csv` files.

A postprocessing happened to trim it even further to strip out columns that we don't need for Postgres import.

48561 rows of the dataset have 'X' in observation count. Some have notes like the following:

> Point Counts at CLNP. Observers Laura Gooch . Total survey interval 05:45-09:40. Start weather: wind NE at 8-12 mph, temp 53 F, cloud cover 0%, precipitation none. End weather: wind N at 8-12 mph, temp 55 F, cloud cover 0%, precipitation none. Notes: Pleasant day, but much cooler than it has been recently, and a little breezy. Bird activity seems to have settled into summer mode. Vegetation is almost fully leafed out, and poison hemlock is already 2-3 m tall in many areas. Midges were plentiful. Breeding codes are noted only for species that do not routinely breed at CLNP. At least 5 deer and lots of bunnies. Four walkers and 4 birders. Species observed during any point count are indicated here by an x, and the actual counts are included with the separately submitted point count data. Counts in this checklist are included only for species that were not seen during any point count.

These rows were omitted from the `trimmed.csv` dataset.
