import fiona
import rasterstats


class ZonalStatistics:

    """
    Calculate zonal statistics using polygons zones from an input shapefile and an input raster.

    :param raster_file:         Full path with filename and extension to the input raster file
    :param shp_file:            Full path with filename and extension to the input polygon shapefile that define zones
    :param out_file:            Full path with filename and extension to the output CSV file
    :param target_field:        Target field name from the input shapefile used to identify each output record
    :param stats_options:       A list of options for statistical output.  These can include:  'min', 'max', 'mean',
                                'count', 'sum', 'std', 'median', 'majority', 'minority', 'unique', 'range', 'nodata',
                                'percentile'; DEFAULT is ['min', 'max', 'mean', 'sum'].
    :param all_touched:         Either True or False (Boolean).  If True, the rasterization strategy will include
                                accounting for all cells in the raster that touch the polygon object.  If False, only
                                raster cells where their centroid falls within the polygon will be counted. DEFAULT is
                                False.
    """

    def __init__(self, raster_file, shp_file, out_file, target_field, all_touched=False,
                 stats_options=['min', 'max', 'mean', 'sum']):

        self.raster_file = raster_file
        self.shp_file = shp_file
        self.out_file = out_file
        self.target_field = target_field
        self.all_touched = all_touched
        self.stats_options = stats_options

    def read_shp(self):
        """
        Read shapefile and extract the target field attributes as a list.
        """
        with fiona.open(self.shp_file) as shp:

            # check to see if field exists in shapefile attribute table
            fields = list(shp.schema['properties'].keys())

            if self.target_field not in fields:
                raise KeyError('KeyError:  Field "{}" not in shapefile attribute table.  Please select valid field. '
                               'Options include:  {}'.format(self.target_field, ', '.join(fields)))

            return [i['properties'][self.target_field] for i in shp]

    def write_csv(self, stats):
        """
        Write output CSV file including field values from target field.

        :param stats:       List of dictionaries containing stats from zonal statistics run.
        """
        # generate a list of field attributes to append to the results
        field_data = self.read_shp()

        with open(self.out_file, 'w') as out:

            for index, row in enumerate(stats):

                if index == 0:

                    hdr = ','.join(row.keys())
                    hdr_list = hdr.split(',')

                    # write header
                    out.write('{},{}\n'.format(self.target_field, hdr))

                s = '{},'.format(field_data[index])

                # assign values according to header since dict is not ordered
                for i in hdr_list:

                    s += '{},'.format(row[i])

                # replace last comma with a return
                s = s[:-1] + '\n'

                out.write(s)

    def zonal_statistics(self):
        """
        Create zonal statistics.
        """
        stats = rasterstats.zonal_stats(self.shp_file,
                                        self.raster_file,
                                        stats=self.stats_options,
                                        all_touched=self.all_touched)

        # write output CSV for the result
        self.write_csv(stats)

        return stats
