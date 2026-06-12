# panels
Automatically enable (Shelly) smart relays when solar energy production has reached a threshold.

`.env` format:
```dotenv
CLOUD_SERVER=https://shelly-<number>-<region>.shelly.cloud
CLOUD_AUTH_KEY=LongStringOfCharacters
CLOUD_DEVICES=device_id1,device_id2,etc
FUSION_SOLAR_URL=https://uni<number>eu<number>.fusionsolar.huawei.com/rest/pvms/web/kiosk/v1/station-kiosk-file?kk=SomeLongString
```