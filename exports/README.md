# Exports

Each exported dataset corresponds to the following queries:

## observed_birds_near_collection_site.csv

Abundance data of birds near each collection site derived from the eBird database.

```sql
-- All observed birds within 3km of each collection location (per season)
-- aggregated by common name.
select
  c.site_name,
	c.location,
	o.season,
	o.common_name,
	sum(o.observation_count) as total_observed
from
	bird_observations o, collections c
where
	st_dwithin(o.location, c.location, 3000) -- within 3km
	and c.season = o.season -- same season
group by
	c.site_name, c.location, o.season, o.common_name
order by season
```

## combined_eaten_birds_at_collection_site.csv

Birds that were "eaten" at each site with all species of culex combined

```sql
-- All birds that were eaten on by collection location (per season)
-- aggregated by common name.
select
  c.site_name,
	c.location,
	c.season,
	c.sequence_results as common_name,
	count(c.sequence_results) as total_eaten
from
	collections c
group by
	c.site_name, c.location, c.season, c.sequence_results
order by season
```

Two other variants were exported, each for a specific culex (pipiens vs restuans)

## skips.csv

Contains collection rows that were skipped in the IPA calculations because we didn't have any eBird density information for that species within 3km of the collection area.
