# Foreach plugin
Adds a `foreach` syntax for the editor, allowing you to quickly loop over an array.

## Syntax :
```
foreach <destination_type> <destination> <source>
```

## Examples :
```
foreach string fruit fruits
```

*Using the `&` symbol will put the key variable in data result mode*
```
foreach struct_Polygon &polygon polygons
```