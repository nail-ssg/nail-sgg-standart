# nail-ssg
Nail. Simple site generator

## config.yml
``` yaml
# config.yml v0.2
core:
  dist: site
  src: src
  currentNamespace: default
  modules:
    static: on
    collections: on
    alias: on
    pages: on
    mixin: on
  main:
    module: main
    options:
scan:
  order:
  - page
  - data
  - static
  pages:
    folder: pages
  types:
  - type: page
    extractData: true
    rules:
    - fileMask = *.html
    - regExp = \.page\.
  - type: data
    extractData: true
    rules:
    - fileMask = *.yml
    - regExp = \.data\.
  - type: static
    extractData: false
    rules:
    - fileMask = *.*

modify:
  order:
  - alias
  - collections
  - mixin
  - pages
  options:
  - pages:
      folder: pages
      dontCopy:
      otherAsStatic: true


builders:
  renders:
  - plain:
  - mustache:
  order:
    - static
    - pages
  static:
    folder: static
  pages:
  - noRename:
    - fileMask = index.html
  - rename:
    - ~\.page~~ # replace '.page' to empty string
    - ~((.*)\.html)~\1/index.html~
```

## page settings
``` yaml
# v0.2
$global:
  alias:
    name: aliasName
    namespace: default
  collections:
    - collectionName1
    - collectionName2
    - collectionName3
$local:
  neighbors:
    - collection: collectionName4
      direction: ascending
      fieldname: dataName1
      useAs: dataName3
      distance: 1
  renders:
    - type: jade
    - type: mustache
  use:
    css:
      from: css
      sort: '+line'
      offset: 0
      count: 10
  load:
    - var1: file1
    - var2: file2
  collections:
    css:
      - href: style1.css
        line: 10.312
      - href: style2.css
        line: 20
    js:
      - href: script1.js
        line: 10.312
      - href: script2.js
        line: 10.313
    load:
      var3: file3
      var4: file4
    loadCollections:
      var5: folder
dataName1: dataValue1
dataName2: dataValue2
```