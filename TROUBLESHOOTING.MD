# TROUBLESHOOTING

## "Permission Denied" on Linux

Linux uses a kernel parameter (net.ipv4.ping_group_range) to restrict who can create ICMP (ping) sockets. From [kernel.org](https://www.kernel.org/doc/Documentation/networking/ip-sysctl.txt):

> ping_group_range - 2 INTEGERS  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Restrict ICMP_PROTO datagram sockets to users in the group range.  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;The default is "1 0", meaning, that nobody (not even root) may  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;create ping sockets.  Setting it to "100 100" would grant permissions  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;to the single group. "0 4294967295" would enable it for the world, "100  
&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;4294967295" would enable it for the users, but not daemons.  

To *temporarily* set this parameter, allowing all users to create ICMP sockets (until next boot):

```
sudo sysctl net.ipv4.ping_group_range='0 4294967295'
```

Some systems (e.g. Debian) may have issues with this, returning:
```
sysctl: setting key "net.ipv4.ping_group_range": Invalid argument
```

In this case, try:
```
sudo sysctl net.ipv4.ping_group_range='0   2147483647'
```

To *permanently* set this parameter:
```
echo "# allow all users to create icmp sockets\n net.ipv4.ping_group_range=0 2147483647" | sudo tee -a /etc/sysctl.d/ping_group.conf
```