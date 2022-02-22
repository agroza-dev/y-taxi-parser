Simple parser.


**Setup**

For graphical user interface mode:
1. Create and fill _**setup/config.py**_ based on example _**setup/config.py.example**_
2. Assure, that `Config.Tg` and `Config.Parser.addresses` is completed.
3. Set `Config.debug_mode = True`
4. Install requirements `pip install -r requirements.txt`
5. run `python main.py`



For command line interface mode:
1. Create and fill _**setup/config.py**_ based on example _**setup/config.py.example**_
2. Assure, that `Config.Tg` and `Config.Parser.addresses` is completed.
3. Set `Config.debug_mode = False`
4. Install requirements `pip install -r requirements.txt`
5. run `python main.py`

Also, you can use docker: `docker-compose up -d`