from pystrictconfig.core import Integer, Float, String, Bool, Map

schema = Map(schema={
    'integer': Integer(),
    'float1': Float(strict=False),
    'float2': Float(),
    'string': String(),
    'bool1': Bool(),
    'bool2': Bool(),
    'bool3': Bool(),
    'bool4': Bool(),
    'bool5': Bool(),
    'bool6': Bool(),
    'bool7': Bool(),
})
