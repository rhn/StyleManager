QGIS Style Manager Plugin
=========================

This plugin allows to manage all styles used in the project as a single style bundle.

**NOTE**: The plugin is experimental and may eat your cat.

Exporting
---------

The plugin will export all visible layers into a directory of your choice, saving their ordering, styles and names.

The styles will be groupped inside subdirectories, named after your layers in the following way:

If your layer is called `name_something`, then it will go into a subdirectory called `name`.

*WARNING*: layers of identical strings in `name` and identical types will overwrite each other. If you have any, rename them before exporting.

Importing
---------

The plugin requires you to have 3 layers in your project (visible or not), called `points`, `lines` and `multipolygons`. These layers will contain data for imported styles.

After loading a `styles.json` file, the base layers will be duplicated and the new styles applied.

Installation
------------

### Requirements

* `pyrcc4` (can be found in PyQt4 devel packages)
* `sphinx-build` for docs and deployment (can be found in python-sphinx packages)

Building
--------

To build the plugin, `cd` to the plugin directory and execute:

```
make
```

To deploy it locally to your QGIS installation:

```
make deploy
```

Make sure that you have enabled experimental plugins in QGIS and it will show up on your plugin list.

Tests
-----

To do automated tests:

```
make test
```

TODO
----

* Implement/fix dialog tests
* Create documentation
* Load raster styles
* Handle errors
