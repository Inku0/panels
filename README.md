# panels
Automatically enable (Shelly) smart relays when solar energy production reaches a threshold.

`.env` format:
```dotenv
CLOUD_SERVER=https://shelly-<number>-<region>.shelly.cloud
CLOUD_AUTH_KEY=LongStringOfCharacters
CLOUD_DEVICES=device_id1,device_id2,etc
FUSION_SOLAR_USERNAME=YourUsername
FUSION_SOLAR_PASSWORD=YourPassw0rd
FUSION_SOLAR_SUBDOMAIN=uni<number>eu5
LATITUDE=12.34
LONGITUDE=56.78
TIMEZONE=Continent/City
```