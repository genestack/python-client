# Python Client Library

### Documentation

   [stable](http://genestack-client.readthedocs.org/en/stable/)

### Installation
   
   - install library
     - `pip install https://github.com/genestack/python-client/archive/stable.zip --upgrade`
   - setup default user
     - `genestack-user-setup init`
   
### Repo

  ```
  docs/                             - folder with documentation sources
  genestack_client/                 - folder with library
  tests/                            - developer tests, require pytest to run.
  genestack-application-manager     - script to connect to application-manager (installed as script)
  genestack-user-setup              - script to setup user (installed as script)
  genestack-uploader                - commandline uploader (installed as script)
  genestack-shell                   - shell (installed as script)
  setup.py                          - installation setup for genestack_client library
  ```

### Generate documentation files

 - install [**sphinx**](http://sphinx-doc.org/) and **sphinx-rtd-theme**
   - `pip install Sphinx sphinx-rtd-theme`
 - `cd docs`
 - `make html`

**Note!** `make` use script `make_shell_docs.py` that generates documentation for shell applications
 
