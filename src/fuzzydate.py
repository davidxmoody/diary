# Try to load dateutil if it is installed, otherwise use strptime
try:
    import dateutil.parser
    def custom_date(date_string):
        #TODO use a reference date (or two) so that today's date doesn't fill in the unspecified bits
        #TODO add an `--on` option which takes one date and then calculates the highest and lowest dates
        #     which that could apply to and passes them to the maximum and minimum date fields
        return dateutil.parser.parse(date_string, fuzzy=True)

except:
    import datetime
    def custom_date(date_string):
        return datetime.datetime.strptime(date_string, '%Y-%m-%d')

