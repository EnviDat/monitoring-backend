from django.db.models.fields import FloatField


# Custom FloatField for LWFMeteo class. Rounds values to hundreths place and converts 'NA' values to null.
class LWFMeteoFloatField(FloatField):
    copy_template = """
        CASE
            WHEN "%(name)s" = 'NA' THEN NULL
            ELSE ROUND(TO_NUMBER(("%(name)s"), '9999.999'), 2) 
        END
    """


# Custom FloatField for LWFStation class. Rounds values to thousandths place and converts 'NA' values to null.
class LWFStationFloatField(FloatField):

    copy_template = """
        CASE
            WHEN "%(name)s" = 'NA' THEN NULL
            ELSE ROUND(TO_NUMBER(("%(name)s"), '99999999999.9999'), 3) 
        END
    """
