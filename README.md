## Yandex.Taxi Fare Monitoring Service

## Overview

The Yandex.Taxi Fare Monitoring Service is a lightweight project designed to automate the authorization process on the taxi.yandex.ru website, parse the cost of a taxi ride between a set of addresses from point A to point B, and send notifications to a Telegram channel based on predefined fare threshold.

## Features

- **User-Friendly Setup:**

    - For graphical user interface mode, create and configure the _**setup/config.py**_ file based on the provided example _**setup/config.py.example**_.
    - Ensure that `Config.Tg` and `Config.Parser.addresses` are correctly filled.
    - Toggle between graphical user interface mode and command line interface mode by setting `Config.debug_mode = True` or `Config.debug_mode = False` respectively.
- **Docker Support:**

    - Alternatively, utilize Docker for seamless deployment with the command: `docker-compose up -d`.
- **Address Parsing and Fare Calculation:**

    - The system parses addresses provided for the starting point (point A) and the destination (point B) to initiate the fare calculation.
    - Using scraping techniques, the service calculates the current fare for the taxi ride based on the provided addresses.
- **Threshold Alerts:**

    - Users can set price treshold in the configuration file.
    - The service monitors the current fare and sends alerts to a Telegram channel if the fare surpasses the treshold or falls below treshold.
- **Flexible Deployment:**

    - Choose between graphical user interface mode for interactive setup or command line interface mode for script-based execution.

## Getting Started

Follow these steps to get started with the Yandex.Taxi Fare Monitoring Service:

1. **User Interface Mode:**

    - Create and configure the _**setup/config.py**_ file.
    - Set `Config.debug_mode = True` for graphical user interface mode.
    - Install requirements: `pip install -r requirements.txt`
    - Run: `python main.py`
2. **Command Line Interface Mode:**

    - Create and configure the _**setup/config.py**_ file.
    - Set `Config.debug_mode = False` for command line interface mode only.
    - Install requirements: `pip install -r requirements.txt`
    - Run: `python main.py`
3. **Docker Mode:**

    - Use Docker for deployment: `docker-compose up -d`

## Configuration

Adjust the configuration file (_**setup/config.py**_) to customize the following settings:

- **Yandex:** Add Yandex account credentials Yandex.Taxi services.
- **Telegram Channel:** Set the Telegram channel details for receiving notifications.
- **Fare Limits:** Define the upper threshold for notifications.

## License

This project is licensed under the MIT License.