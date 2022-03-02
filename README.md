# zuvio roll call

自己使用

我沒有課是非GPS點名，非GPS不清楚有沒有bug
> 確認可以使用

config.json 填入 zuvio 帳號密碼即可使用

download release or `python zuvio.py`
2020/09/13 可用


## Loop 選項

主要用在 Server 持續運行服務，只要老師開點名就自動點，點完不會關閉程式，而會繼續運行
注意，開啟這個選項後撥放音樂功能會自動關閉。

`waitSecAfterSuccess 可以設定成功點名後間隔多久再次檢查有無點名

## Docker usage
![Alt text](https://img.shields.io/docker/v/o2range/zuvio-auto?style=flat-square)
```
docker pull o2range/zuvio-auto
```

```shell
docker run --env USER=your_username --env PASSWD=your_password --env LINE_NOTIFY_TOKEN=token zuvio-auto --LAT=lat --LNG=lng
```

## ENV LIST

```
USER=使用者帳號   
PASSWD=使用者密碼   
LINE_NOTIFY_TOKEN=LINE Notify TOKEN  
LAT=學校緯度  
LNG=學校經度  
WAITSEC=檢查點名間隔  
FULLMODE=所有課程模式(bool)  
LINE_NOTIFY_ON=使否傳送Line Notify(bool)  
LOOP_ON=無限循環模式(bool)  
WAIT_SEC_AFTER_CALL=完成點名後冷卻秒數  
```