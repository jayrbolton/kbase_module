# KBase Module Utils

This is a Python package that provides utilities for writing [KBase](https://kbase.us) bioinformatics modules that can run in the narrative or be executed by other modules.

## Installation

Install with pip:

```
pip install kbase_module
```

## Usage

### Defining module methods

Use the `kbase_module.method` decorator:

```py
from kbase_module import method

@method
def method_name(params):
    return 'Hello world'
```

The decorator uses the name of your function, which must correspond to an entry in your `kbase_methods.json`.

#### Return value and reports

TODO

* If you return a string, it generates a report with a text message
* If you return a dict with the X key... TODO

### Running other KBase modules

Use the `kbase_module.run` function to run other KBase modules. The other module must be registered in the catalog in order to run it.

```py
import kbase_module

@kbase_module.method
def my_method(params):
    results = kbase_module.run(
        module='AssemblyUtil',
        method='get_assembly_as_fasta',
        params={'ref': params['assembly_object'], 'filename': 'downloaded_assembly.fasta'}
    )
    path = results['path']
    assembly_name = results['assembly_name']
    return "Downloaded %s to path %s" % (assembly_name, path)
```

#### Parameters

* `params` - required - dict - parameters to pass to the method
* `module` - required - string - name of the registered module
* `method` - required - string - name of the method to run
* `version` - optional (defaults to latest) - string - version of the module to run
* `tag` - optional (defaults to release) - string - tag of the module to run

The function uses the `KBASE_ENDPOINT` environment variable to access modules and services.

#### Return value

The return value is a Python dict representing the JSON object that gets returned from the module.

### Logging

Use the functions in `kbase_module.logging` to do logging in your module:

```py
from kbase_module.logging import info, debug, error

info('This is an informational, status message')
debug('This is a debugging message')
error('This is an error message')
```

## Development

Run tests with `make test`
