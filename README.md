# ZoomPlus:heavy_plus_sign:

## Setting Up environment
- Linux
    - `conda create --name env python=3.7`
    - `conda activate env`
    - `pip install -r requirements.txt`
- Windows
    - `cd env\Scripts`
    - `activate`
    - `cd ../../`

## Run project
- Linux 
    - Uncomment line 24
    `driver=Chrome("./chromedriver.exe",options=options)`
    - Comment line 26
    `driver=Chrome(ChromeDriverManager().install(),options=options)`
- Windows
    - Uncomment line 26 
    `driver=Chrome(ChromeDriverManager().install(),options=options)`
    - Comment line 24
    `driver=Chrome("./chromedriver.exe",options=options)`
    
`python app.py`