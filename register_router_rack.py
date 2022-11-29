import keyring
import lzma
import os
import pymysql
import subprocess
import sys
import tarfile

from datetime import datetime
from pick import pick
from time import sleep

user = os.getlogin()
dbpw = keyring.get_password("172.28.88.47", "simdbuploader")


try:
    os.listdir(f"/home/{user}/labelfiles")
except Exception:
    print("labelfiles folder was not found. Creating folder")
    os.mkdir(f"/home/{user}/labelfiles")


try:
    ps = subprocess.Popen('sudo lpinfo -m', stdout=subprocess.PIPE, shell=True)
    drivers_check = subprocess.check_output(('grep', 'TTP-644MT'), stdin=ps.stdout)
    ps.wait()
    drivers_check = drivers_check.decode().strip()
except Exception:
    print(f"Printer drivers not installed. Installing..")
    with lzma.open('drivers.tar.xz') as fd:
        with tarfile.open(fileobj=fd) as tar:
            content = tar.extractall('drivers')
    os.chdir('drivers')
    cmd = 'sudo ./install-driver'.split()
    subprocess.run(cmd)


try:
    ps = subprocess.Popen('lpstat -p -d', stdout=subprocess.PIPE, shell=True)
    printer_check = subprocess.check_output(('grep', 'TTP-644MT'), stdin=ps.stdout)
    ps.wait()
    printer_check = printer_check.decode().strip()
except Exception:
    print(f"Printer TTP-644MT not installed. Installing..")
    cmd = 'sudo lpadmin -p TTP-644MT -E -m tscbarcode/TTP-644MT.ppd -v lpd://172.28.88.43/queue -o PageSize=Custom.60x30mm'.split()
    subprocess.run(cmd)


try:
    ps = subprocess.Popen('lpstat -p -d', stdout=subprocess.PIPE, shell=True)
    printer_check = subprocess.check_output(('grep', 'ME340_lager'), stdin=ps.stdout)
    ps.wait()
    printer_check = printer_check.decode().strip()
except Exception:
    print(f"Printer ME340_lager not installed. Installing..")
    cmd = 'sudo lpadmin -p ME340_lager -E -m tscbarcode/ME340.ppd -v lpd://172.28.88.46/queue -o PageSize=Custom.60x30mm'.split()
    subprocess.run(cmd)


try:
    ps = subprocess.Popen('lpstat -p -d', stdout=subprocess.PIPE, shell=True)
    printer_check = subprocess.check_output(('grep', 'ME340_production'), stdin=ps.stdout)
    ps.wait()
    printer_check = printer_check.decode().strip()
except Exception:
    print(f"Printer ME340_production not installed. Installing..")
    cmd = 'sudo lpadmin -p ME340_production -E -m tscbarcode/ME340.ppd -v lpd://172.28.88.60/queue -o PageSize=Custom.60x30mm'.split()
    subprocess.run(cmd)


try:
    ps = subprocess.Popen('lpstat -p -d', stdout=subprocess.PIPE, shell=True)
    printer_check = subprocess.check_output(('grep', 'Zebra_ZT230_production'), stdin=ps.stdout)
    ps.wait()
    printer_check = printer_check.decode().strip()
except Exception:
    print(f"Printer Zebra_ZT230_production not installed. Installing..")
    cmd = 'sudo lpadmin -p Zebra_ZT230_production -E -m drv:///sample.drv/zebra.ppd -v socket://172.28.88.44:9100 -o PageSize=Custom.101x152mm'.split()
    subprocess.run(cmd)


try:
    ps = subprocess.Popen('lpstat -p -d', stdout=subprocess.PIPE, shell=True)
    printer_check = subprocess.check_output(('grep', 'Zebra_ZT230_lager'), stdin=ps.stdout)
    ps.wait()
    printer_check = printer_check.decode().strip()
except Exception:
    print(f"Printer Zebra_ZT230_lager not installed. Installing..")
    cmd = 'sudo lpadmin -p Zebra_ZT230_lager -E -m drv:///sample.drv/zebra.ppd -v socket://172.28.88.45:9100 -o PageSize=Custom.101x152mm'.split()
    subprocess.run(cmd)


def sqlquery(query): #column,table,where,value
    db = pymysql.connect(host="172.28.88.47",user="simdbuploader",password=dbpw,database="simdb")
    cursor = db.cursor()
    #cursor.execute(f"SELECT {column} FROM simdb.product_label WHERE pn='{itemnumber}'")
    cursor.execute(f"{query}")
    try:
        result = cursor.fetchone()[0]
    except Exception:
        result = False
    return(result)
    db.commit()
    db.close()


def dbupload(cmd1, cmd2):
    db = pymysql.connect(host="172.28.88.47",user="simdbuploader",password=dbpw,database="simdb")
    cursor = db.cursor()
    #sql= "INSERT INTO simdb.racks (customerid, projectid, articlenumber, rackserial, routerserial, customerserialprefix, customerserial) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    #val = (serial, projectid, sap, simids['simid1'], sims['sim1'], simids['simid2'], sims['sim2'], simids['simid3'], sims['sim3'], simids['simid4'], sims['sim4'], simids['simid5'], sims['sim5'], simids['simid6'], sims['sim6'], simids['simid7'], sims['sim7'], simids['simid8'], sims['sim8'], simids['simid9'], sims['sim9'], simids['simid10'], sims['sim10'], simids['simid11'], sims['sim11'], simids['simid12'], sims['sim12'], simids['simid13'], sims['sim13'], simids['simid14'], sims['sim14'], simids['simid15'], sims['sim15'], simids['simid16'], sims['sim16'], firmwares['modemfirmware1'], firmwares['modemfirmware2'], firmwares['modemfirmware3'], firmwares['modemfirmware4'], firmwares['modemfirmware5'], firmwares['modemfirmware6'], imeis['imei1'], imeis['imei2'], imeis['imei3'], imeis['imei4'], imeis['imei5'], imeis['imei6'], modems['modem1'], modems['modem2'], modems['modem3'], modems['modem4'], modems['modem5'], modems['modem6'], wifis['wifi0'], wifis['wifi1'], mac, imp, mo)
    cursor.execute(cmd1, cmd2)
    db.commit()
    cursor.close()
    db.close()


while True:
    title = 'Select printer: '
    options = ['TTP-644MT', 'ME340_production', 'Zebra_ZT230_production', 'ME340_lager', 'Zebra_ZT230_lager']
    printer, index = pick(options, title)
    title = 'Choose label size: '
    options = ['60x30mm', '100x20mm', '101x152mm']
    labelsize, index = pick(options, title)
    sap = input('Enter your SAP number: ')
    serial = input('Enter router serial: ')
    serialcheck = sqlquery(f"SELECT rackid FROM simdb.racks WHERE routerserial='{serial}'")
    #serialcheck = sqlquery('rackid','racks','routerserial',serial)
    #try:
    if serialcheck:
        print('Serial already exists in database')
    else:
        customerid = sqlquery(f"SELECT customerid FROM simdb.custspecificracks WHERE articlenumber='{sap}'")
        projectid = sqlquery(f"SELECT projectid FROM simdb.custspecificracks WHERE articlenumber='{sap}'")
        #customerid = sqlquery('customerid','custspecificracks','articlenumber',sap)
        #projectid = sqlquery('projectid','custspecificracks','articlenumber',sap)
        racks = sqlquery("SELECT MAX(rackserial)+1 FROM simdb.racks")
        racks=int(racks)
        rackserial=str(racks).zfill(6)
        print(customerid, projectid, rackserial)
        customerspecific = sqlquery(f"SELECT articlenumber FROM simdb.custspecificracks WHERE articlenumber='{sap}'")
        if customerspecific == False:
            unitname = "Router Rack"
            customerserial = None
        else:
            unitname = sqlquery(f"SELECT custarticlename FROM simdb.custspecificracks WHERE articlenumber='{sap}'")
            print(unitname)
            sapdb = sqlquery(f"SELECT custarticlenumber FROM simdb.custspecificracks WHERE articlenumber='{sap}'")
            print(sapdb)
            customerserialprefix = sqlquery(f"SELECT serialprefix FROM simdb.custspecificracks WHERE articlenumber='{sap}'")
            #customerserialprefix = customerserialprefix.split('.')[0]
            customerserial = str(sqlquery(f"SELECT MAX(customerserial)+1 FROM simdb.racks WHERE customerserial IS NOT NULL AND customerserialprefix LIKE '{customerserialprefix}'")).split('.')[0]
            customerserial = customerserial.zfill(4)
            print(customerserialprefix,customerserial)
            print(type(customerserial))
        if customerserial:
            dbupload("INSERT INTO simdb.racks (customerid, projectid, articlenumber, rackserial, routerserial, customerserialprefix, customerserial) VALUES (%s, %s, %s, %s, %s, %s, %s)", (f"{customerid}", f"{projectid}", f"{sap}", f"{rackserial}", f"{serial}", f"{customerserialprefix}", f"{customerserial}"))
        else:
            dbupload("INSERT INTO simdb.racks (customerid, projectid, articlenumber, rackserial, routerserial) VALUES (%s, %s, %s, %s, %s)", (f"{customerid}", f"{projectid}", f"{sap}", f"{rackserial}", f"{serial}"))
            #sqlquery(f"INSERT INTO simdb.racks (customerid, projectid, articlenumber, rackserial, routerserial) VALUES ({customerid}, {projectid}, {sap}, {rackserial}, {serial})")
        rackid = sqlquery(f"SELECT rackid FROM simdb.racks WHERE rackserial LIKE '{rackserial}'")
        if rackid:
            print('Success!')
            if customerserial:
                if customerserialprefix:
                    customerserialprefix=str(customerserialprefix)
                    customerserial=str(customerserial)
                    concatenateserial = customerserialprefix+customerserial
                else:
                    concatenateserial = customerserial
                cmd = "glabels-batch-qt  "\
                    f"/mnt/fs/Icomera/Line/Supply Chain/Production/Glabels/Templates/router_rack.glabels  "\
                    f"-D  serial={serial}  "\
                    f"-D  sap={sap}  "\
                    f"-D  sapdb={sapdb}  "\
                    f"-D  name={unitname}  "\
                    f"-D  custs={concatenateserial}  "\
                    f"-D  rackserial={rackserial}  "\
                    f"-o  /home/{user}/labelfiles/{serial}.pdf".split("  ")
                subprocess.run(cmd)
                logisticsQR = str(serial)+" - "+str(rackserial)
                cmd = "glabels-batch-qt  "\
                    f"/mnt/fs/Icomera/Line/Supply Chain/Production/Glabels/Templates/logisticslabel.glabels  "\
                    f"-D  serial={logisticsQR}  "\
                    f"-o  /home/{user}/labelfiles/{serial}l.pdf".split("  ")
                subprocess.run(cmd)
                sleep(1)
                cmd = f"lp -n 2 -c /home/{user}/labelfiles/{serial}.pdf -c /home/{user}/labelfiles/{serial}l.pdf -d {printer} -o media={labelsize}".split()
                subprocess.run(cmd)
        else:
            print('Upload failed!')
