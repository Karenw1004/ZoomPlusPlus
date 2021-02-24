# ZoomPlus:heavy_plus_sign:
[![Python 3.7](https://img.shields.io/badge/python-3.7-blue.svg)](https://www.python.org/downloads/release/python-379/)

## Setting Up environment
- Linux
    - `conda create --name env python=3.7`
    - `conda activate env`
    - `pip install -r requirements.txt`
- Windows
    - `virtualenv -p 3.7 env`
    - `cd env\Scripts`
    - `activate`
    - `cd ../../`

## Run project
- Go to host.py
    - Linux 
        - Uncomment line 34 <br>
        `driver=Chrome("./chromedriver.exe",options=options)`
        - Comment line 36 <br>
        `driver=Chrome(ChromeDriverManager().install(),options=options)`
    - Windows
        - Uncomment line 36 <br>
        `driver=Chrome(ChromeDriverManager().install(),options=options)`
        - Comment line 34 <br>
        `driver=Chrome("./chromedriver.exe",options=options)` 
 ```python
python app.py
```
