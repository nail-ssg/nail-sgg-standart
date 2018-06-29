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
  - pages
  - data
  - static
  types:
    page:
      folder: pages
      extractData: true
      rules:
      - fileMask = *.html
      - regExp = \.page\.
    data:
      extractData: true
      rules:
      - fileMask = *.yml
      - regExp = \.data\.
    static:
      extractData: false
      rules:
      - fileMask = *.*

modify:
  order:
  - alias
  - collections
  - loads
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
# v0.3
$load:                                      # nail_ssg_standard.load
  .: data_path1                             # 
  propertyName: data_path2                  # 
  propertyName/subProperty: data_path3      # 
$global:                                    # 
  alias:                                    # nail_ssg_standard.alias
    name: aliasName                         # 
    namespace: default                      # 
  collections:                              # nail_ssg_standard.collections
    - collectionName1                       # 
    - collectionName2                       # 
    - collectionName3                       # 
$local:                                     # 
  neighbors:                                # nail_ssg_standard.collections
    - collection: collectionName4           # 
      direction: ascending                  # 
      fieldname: dataName1                  # 
      useAs: dataName3                      # 
      distance: 1                           # 
  renders:                                  # nail_ssg_standard.renders
    - type: jade                            # 
    - type: mustache                        # 
  use:                                      # nail_ssg_standard.collections
    css:                                    # 
      from: css                             # 
      sort: ['+line','-href']               # 
      page: 0                               # 
      page_length: 10                       # 
  collections:                              # nail_ssg_standard.collections
    css:                                    # 
      - href: style1.css                    # 
        index: a                            # 
      - href: style2.css                    # 
        index: b                            # 
    js:                                     # 
      - href: script1.js                    # 
        index: a                            # 
      - href: script2.js                    # 
        index: b                            # 
    load:                                   # 
      var3: file3                           # 
      var4: file4                           # 
    loadCollections:                        # 
      var5: folder                          # 
property1: propertyValue1                   # nail_ssg_standard.main
property2: propertyValue2                   # 
```