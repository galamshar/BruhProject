## AituForum
Forum for students ASTANA IT UNIVERSITY, where students can discuss general topics of interest and create different topics on different topics.

## How To Deploy

Make sure you have installed and configured docker in your environment. After that, you can run the below commands from the directory and get started with the AituForum immediately.

```docker
docker pull minio/minio
docker run -p 9000:9000 minio/minio server /data
```
You should be able to browse components of the Minio by using the below URLs :
```plaintext
Minio : http://webapi:9000/
```
Create new bucket and set in the services.py your Minio parameters: 
![alt services.py](https://i.imgur.com/8Ap5imv.png)

After that in the settings.py set your database parameters:
![alt dbsettings](https://i.imgur.com/iWZ1340.png)

And set your broker parameters in the background.py:
![alt brokersett](https://i.imgur.com/FmsHkIM.png)

Finally, just run python server:
```plaintext
django-admin runserver
```

## Architecture
![alt Database](https://i.imgur.com/Fftd2aM.png)

## Features

- Auto creating / settling events from broker data with RabbitMQ
- Media storage “minio” integration
- Bet to event  / Sell bet to special price which calculated with special formula

## Platforms

- Web

## Technologies for development

- Python / Django
- Jinja2
- RabbitMQ
- PostgreSQL
- Minio
- Jquery


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.
