#!/usr/bin/python

from ldap3 import Server, Connection, ALL, NTLM
server=Server('<LDAP_server>', get_info=ALL)
conn=Connection(server,user='<domain>\\<username>',password='xxxx',authentication=NTLM,auto_bind=True)
conn.search('OU=someou,DC=domain,DC=domain','(&(objectclass=person)(sAMAccountName=<whatever>))',attributes=['sAMAccountName','name'])

print "There are %s users" % (len(conn.entries))
#for i in range(0,len(conn.entries)):
#       print "User:"
#       print "\t %s" % (conn.entries[i]['name'])
#       print "\t %s" % (conn.entries[i]['sAMAccountName'])

mycsv=open("userdata.csv","w")
mycsv.write("username, full_name\n")
for i in range(0,len(conn.entries)):
        fullname=str(conn.entries[i]['name'])
        mycsv.write("%s,%s,%s\n" % (conn.entries[i]['sAMAccountName'], fullname.replace(",",".")))
