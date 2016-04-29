#### An Ambari service for OpenTSDB
Ambari service for easily installing and managing OpenTSDB on HDP cluster

Limitations:

- This is not an officially supported service and *is not meant to be deployed in production systems*. It is only meant for testing demo/purposes
- It does not support Ambari/HDP upgrade process and will cause upgrade problems if not removed prior to upgrade

Author: [Ali Bajwa](https://www.linkedin.com/in/aliabajwa)

##### Setup

- Download HDP latest sandbox VM image (.ova file) from [Hortonworks website](http://hortonworks.com/products/hortonworks-sandbox/)
- Import ova file into VMWare and ensure the VM memory size is set to at least 8GB
- Now start the VM
- After it boots up, find the IP address of the VM and add an entry into your machines hosts file e.g.
```
192.168.191.241 sandbox.hortonworks.com sandbox    
```
- Connect to the VM via SSH (password hadoop)
```
ssh root@sandbox.hortonworks.com
```

- Start HBase service from Ambari and ensure Hbase is up and root has authority to create tables. You can do this by trying to create a test table
```
hbase shell

create 't1', 'f1', 'f2', 'f3'
```

  - If this fails with the below, you will need to provide appropriate access via Ranger (http://sandbox.hortonworks.com:6080)
  ```
  ERROR: org.apache.hadoop.hbase.security.AccessDeniedException: Insufficient permissions for user 'root (auth:SIMPLE)' (global, action=CREATE)
  ```
  
- To deploy the OpenTSDB service, run below
```
VERSION=`hdp-select status hadoop-client | sed 's/hadoop-client - \([0-9]\.[0-9]\).*/\1/'`
sudo git clone https://github.com/hortonworks-gallery/ambari-opentsdb-service.git /var/lib/ambari-server/resources/stacks/HDP/$VERSION/services/OPENTSDB
```
- Restart Ambari
```
#on sandbox
sudo service ambari restart

#on non-sandbox clusters  
sudo service ambari-server restart
sudo service ambari-agent restart
```
- Then you can click on 'Add Service' from the 'Actions' dropdown menu in the bottom left of the Ambari dashboard:
![Image](../master/screenshots/service-install.png?raw=true)

On bottom left -> Actions -> Add service -> check OpenTSDB server -> Next -> Next -> Customize as needed -> Next -> Deploy

You can customize the port, ZK quorum, ZK dir in the start command. **Note that Hbase must be started if the option to automatically create OpenTSDB schema is selected**

![Image](../master/screenshots/service-install-options.png?raw=true)

- On successful deployment you will see the OpenTSDB service as part of Ambari stack and will be able to start/stop the service from here:
![Image](../master/screenshots/service-status.png?raw=true)

- You can see the parameters you configured under 'Configs' tab
![Image](../master/screenshots/service-config.png?raw=true)

- One benefit to wrapping the component in Ambari service is that you can now monitor/manage this service remotely via REST API
```
export SERVICE=OPENTSDB
export PASSWORD=admin
export AMBARI_HOST=sandbox.hortonworks.com
export CLUSTER=Sandbox

#get service status
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X GET http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#start service
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Start $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "STARTED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#stop service
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Stop $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE
```


### Remove service

- To remove the OpenTSDB service: 
  - Stop the service via Ambari
  - Unregister the service by running below from Ambari node
  
    ```
#Ambari password
export PASSWORD=admin
#Ambari host
export AMBARI_HOST=localhost
export SERVICE=OPENTSDB

#detect name of cluster
output=`curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari'  http://$AMBARI_HOST:8080/api/v1/clusters`
CLUSTER=`echo $output | sed -n 's/.*"cluster_name" : "\([^\"]*\)".*/\1/p'`

#unregister service from ambari
curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X DELETE http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#if above errors out with 500 error code, run below first to fully stop the service then re-run above to unregister service from Ambari
#curl -u admin:$PASSWORD -i -H 'X-Requested-By: ambari' -X PUT -d '{"RequestInfo": {"context" :"Stop $SERVICE via REST"}, "Body": {"ServiceInfo": {"state": "INSTALLED"}}}' http://$AMBARI_HOST:8080/api/v1/clusters/$CLUSTER/services/$SERVICE

#now restart ambari

#sandbox
service ambari restart

#non-sandbox
service ambari-server restart

    ```
  - Remove artifacts 
  
    ```
    rm -rf /root/opentsdb
    rm -rf /var/lib/ambari-server/resources/stacks/HDP/2.2/services/opentsdb-service/
    ```


---------------

#### Import stock data

- Use below sample code (taken from [here](http://trading.cheno.net/downloading-google-intraday-historical-data-with-python/)) to pull 30 day intraday stock prices for a few securities in both OpenTSDB and csv formats
```
cd
/bin/rm -f prices.csv
/bin/rm -f opentsd.input
wget https://raw.githubusercontent.com/abajwa-hw/opentsdb-service/master/scripts/google_intraday.py
python google_intraday.py AAPL > prices.csv
python google_intraday.py GOOG >> prices.csv
python google_intraday.py HDP >> prices.csv
python google_intraday.py ORCL >> prices.csv
python google_intraday.py MSFT >> prices.csv
```

- Review opentsd.input which contains the stock proces in OpenTSDB-compatible format
```
tail opentsd.input
```

- Import data from opentsd.input into OpenTSDB
```
/root/opentsdb/build/tsdb import opentsd.input --zkbasedir=/hbase-unsecure --zkquorum=localhost:2181 --auto-metric
```

-----------  


#### Open WebUI and import stock data

- The OpenTSDB webUI login page should be at the below link (or whichever port you configured) 
http://sandbox.hortonworks.com:9999

- Query the data in OpenTSDB webUI by entering values for:
  -  From: pick a date from 3 weeks ago
  - To: pick todays date
  - Check Autoreload
  - Metric: (e.g. volume)
  - Tags: (e.g. symbol GOOG)
  - You can similarly create multiple tabs 
    - Tags: symbol ORCL
    - Tags: symbol AAPL    

- To make the charts smoother:
  - Under Style tab, check the 'Smooth' checkbox
  - Under Axes tab, check the 'Log scale' checkbox

- You can also open it from within Ambari via [iFrame view](https://github.com/abajwa-hw/iframe-view)
![Image](../master/screenshots/service-view.png?raw=true)

