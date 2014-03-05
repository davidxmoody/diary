# Try to load dateutil if it is installed, otherwise use strptime
try:
    import dateutil.parser
    def custom_date(date_string):
        return dateutil.parser.parse(date_string, fuzzy=True)

except:
    import datetime
    def custom_date(date_string):
        return datetime.datetime.strptime(date_string, '%Y-%m-%d')
