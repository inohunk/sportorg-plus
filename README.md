# SportOrg

### Packages

- PyQt5
- [sireader](https://pypi.python.org/pypi/sireader/1.0.1)
- jinja2
- [polib](http://polib.readthedocs.io/en/latest/quickstart.html)

Install packages
```
pip install package-name

pip install sireader
```

or

```
pip install -t lib -r requirements.txt
```

### Struct

```
<sportorg>/
    data/
    docs/
    log/
    templates/
    python/
    lib/
    img/
        icon/
    languages/
        <lang>/
            LC_MESSAGES/
                sportorg.po
    sportorg/
        core/
        gui/
        models/
        modules/
        lib/
        utils/
```

![Mainwindow sportorg](img/mainwindow.png)

![Dialogedit sportorg](img/dialogedit.png)

### build `go`

[josephspurrier](https://github.com/josephspurrier/goversioninfo) for build `.syso`

```
./goversioninfo -icon=img/icon/sportorg.ico

go build -ldflags="-H windowsgui" -o SportOrg.exe
```