from django.db.models.fields import FloatField


# Custom FloatField for LWF Meteo data. Rounds values to hundreths place and converts 'NA' values to null.
class LWFMeteoFloatField(FloatField):
    copy_template = """
        CASE
            WHEN "%(name)s" = 'NA' THEN NULL
            ELSE ROUND(TO_NUMBER(("%(name)s"), '9999.999'), 2) 
        END
    """