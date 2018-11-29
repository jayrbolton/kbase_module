
class MissingMethod(Exception):

    def __init__(self, method_name, schema):
        self.name = method_name
        self.available = list(schema.keys())

    def __str__(self):
        return 'Missing method "%s". Defined methods: %s' % (self.name, self.available)
