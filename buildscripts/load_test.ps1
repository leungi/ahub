param([Int32]$node=1) 
$ip=get-WmiObject Win32_NetworkAdapterConfiguration|Where {$_.Ipaddress.length -gt 1} 
$thisip=$ip.ipaddress[0]
docker run qunis/ahub_artillery artillery quick -c 5 -kn 5 https://172.22.208.1/node$node/thread