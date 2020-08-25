from django.db.models.fields import FloatField


class LWFMeteoFloatField(FloatField):
    copy_template = """
        CASE
            WHEN "%(name)s" = 'NA' THEN NULL
            ELSE TO_NUMBER(("%(name)s"), '9999.999') 
        END
    """