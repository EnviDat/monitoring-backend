from django.db.models.fields import FloatField, DateTimeField


class CustomFloatField(FloatField):
    copy_template = """
        CASE
            WHEN "%(name)s" = '999' THEN NULL
            WHEN "%(name)s" = '999.0' THEN NULL
            WHEN "%(name)s" = '999.00' THEN NULL
            WHEN "%(name)s" = '999.000' THEN NULL
            WHEN "%(name)s" = '999.0000' THEN NULL
            WHEN "%(name)s" = '-999' THEN NULL
            WHEN "%(name)s" = 'NaN' THEN NULL
            ELSE ROUND(TO_NUMBER(("%(name)s"), '9999.999'), 2) 
        END
    """


class MeteoDateField(DateTimeField):
    copy_template = """
        CASE
            WHEN "%(name)s" = '' THEN NULL
            ELSE to_timestamp("%(name)s", 'YYYY-MM-DDTHH24:MI:SS') /* Meteoio CSV's date pattern */
        END
    """




