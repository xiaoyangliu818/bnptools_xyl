"""
Created on Wed Jul 28 14:32:26 2021

@author: graceluo

Function to setup scan, interact with PV mostly
"""
#!/home/beams/USERBNP/.conda/envs/py36/bin/python

from pvObjects import getPVobj, scan2RecordDetectorTrigerPVs, getEiger, definePVs
from misc import getCurrentTime
import os, time, sys, datetime
import numpy as np
from epics import PV, caget, caput, cainfo

class pvComm():
    def __init__(self, userdir = None, log = 'log.txt'):
        self.allpvs = definePVs()    #all pvs used
        self.pvs = getPVobj()
        self.eiger = getEiger()
        if userdir is None:
            self.userdir = self.getDir()
        else:
            self.userdir = userdir
        self.logfilepath = os.path.join(self.userdir, log)

        self.logfid = open(self.logfilepath, 'a')   #create a log file
            
    def logger(self, msg):
        sys.stdout.write(msg)
        sys.stdout.flush()
        if self.logfid.closed:
            self.logfid = open(self.logfilepath, 'a')
        self.logfid.write(msg)
        self.logfid.flush()   #write 'msg' to log file immdiately 
    
    def getDir(self):
        return '/home/beams/USERBNP/scripts/graceluo/bnp_GUI/bnpGUI_noPV/log'
        #fs = self.pvs['filesys'].pv.value
        #fs = fs.replace('//micdata/data1', '/mnt/micdata1')
        #return os.path.join(fs, self.pvs['subdir'].pv.value.replace('mda', ''))
    
    #-----------------current directory--------------------
    def cur_dir(self):
        self.syspv = self.allpvs['filesys']
        self.folder = PV(self.syspv).get()
        return self.folder

        
    def initCurLineTimer(self):
        self.pvs['cur_lines'].time_pre = datetime.datetime.now()
        self.pvs['cur_lines'].time_delta = 0
        
    def get1DTime(self):
        return self.pvs['1D_time'].pv.get()
        
    def getCurLineTimeStamp(self):
        return self.pvs['cur_lines'].time_pre
    
    def getBDAx(self):
        return 0
        #return np.round(self.pvs['BDA_pos'].pv.value, 2)
    
    def getSMAngle(self):
        return 0
        #return np.round(self.pvs['sm_rot_Act'].pv.value, 2)
    
    def getTomoAngle(self):
        return 0
        #return np.round(self.pvs['tomo_rot_Act'].pv.value, 2)
    
    def scanPause(self):
        self.pvs['wait'].pv.put(1)
    
    def scanResume(self):
        self.pvs['wait'].pv.put(0)
        
    def scanAbort(self):
        self.pvs['abort'].put_callback(1)
        
    def resetDetector(self, ptychoEnable):
        time.sleep(1)
        self.pvs['xmap_stp'].put_callback(1)
        time.sleep(1)
        self.pvs['netCDF_stp'].put_callback(0)
        time.sleep(1)
        self.pvs['mcs_stp'].put_callback(0)
        
        if ptychoEnable:
            self.eiger.cam.Acquire = 0
            time.sleep(1)
            self.eiger.fileIO.Capture = 0
            time.sleep(1)
        
    def updateDetectorTriger(self, ptychoEnable):
        pass
        #s = self.pvs['scan2Record']
        #dtriger_pvs = scan2RecordDetectorTrigerPVs()
        #s.T1PV = dtriger_pvs['scan1']
        #s.T4PV = ''
        #s.T2PV = dtriger_pvs['eigerAcquire'] if ptychoEnable else ''
        #s.T3PV = dtriger_pvs['eigerFileCapture'] if ptychoEnable else ''

            
    def updateEigerFileIO(self, filename, num_pts):
        self.eiger.fileIO.setFileName(filename)
        self.eiger.fileIO.AutoIncrement = 1
        self.eiger.fileIO.NumCapture = num_pts
        self.eiger.fileIO.FileNumber = 0
        
    def updateEigerCam(self, acquireTime, num_img, trig_mode, num_trig):
        self.eiger.cam.AcquirePeriod = acquireTime
        self.eiger.cam.NumImages = num_img
        self.eiger.cam.TriggerMode = trig_mode
        self.eiger.setNumTriggers(num_trig)
        
    def getNumPtsPerLine(self):
        return self.pvs['tot_pts_perline'].pv.get()
        
    def logCryoTemp(self):
        temp_pv = ['CryoCon1:In_1', 'CryoCon1:In_2', 'CryoCon1:In_3', 'CryoCon3:In_2', 'CryoCon3:Loop_2']
        s = ['%s: %.2f'%(t, self.pvs[t].pv.value) for t in temp_pv]
        s = ', '.join(s)
        msg = getCurrentTime() + ': ' + s + '\n'
        self.logger('%s'%msg)

    
    def changeTomoRotate(self, theta):
        curr_angle = np.round(self.pvs['tomo_rot_Act'].pv.value, 2)
        t = getCurrentTime()
        self.logger('%s; Changing tomo rotation angle from to %.2f to %.2f\n'%(t, curr_angle, theta))
        self.pvs['tomo_rot_Act'].put_callback(theta)
    
    def changeSMRotate(self, theta):
        curr_angle = np.round(self.pvs['sm_rot_Act'].curr_value, 2)
        t = getCurrentTime()
        self.logger('%s; Changing sample rotation angle from to %.2f to %.2f\n'%(t, curr_angle, theta))
        self.pvs['sm_rot_Act'].put_callback(theta)
    
    def blockBeamBDA(self, BDA):
        bda_pos = BDA - 500
        t = getCurrentTime()
        self.logger('%s: Move BDA to block position at: %.3f\n'%(t, bda_pos))
        self.pvs['BDA_pos'].put_callback(bda_pos)
        
    def openBeamBDA(self, BDA):
        self.logger('%s: Move BDA to open position at: %.3f\n'%(getCurrentTime(), BDA))
        self.pvs['BDA_pos'].put_callback(BDA)
    
    def changeXYcombinedMode(self):        
        self.logger('%s; Changing XY scan mode to combined motion\n'%(getCurrentTime()))
        self.pvs['x_motorMode'].pv.put(0)
        self.pvs['y_motorMode'].pv.put(0)
        
    def changeXtoCombinedMode(self, waittime=0.5):        
        self.logger('%s; Changing XY scan mode to combined motion\n'%(getCurrentTime()))
        self.pvs['x_motorMode'].pv.put(0) 
        time.sleep(waittime)
        
    def changeXtoPiezolMode(self):
        self.logger('%s: Changing X scan mode to Piezo only\n'%(getCurrentTime()))
        self.pvs['x_motorMode'].pv.put(2)

    def setXYcenter(self):
        self.logger('%s: Update the current position as the center of'\
                    'the scan.\n'%(getCurrentTime()))
        x_rqs = self.pvs['x_center_Rqs'].pv.get()
        y_rqs = self.pvs['y_center_Rqs'].pv.get()
        self.pvs['x_updatecenter'].pv.put(round(x_rqs, 2))
        self.pvs['y_updatecenter'].pv.put(round(y_rqs, 2))
        self.logger('%s: X_center valute: %.2f \n'%(getCurrentTime(), x_rqs))
        self.logger('%s: Y_center valute: %.2f \n'%(getCurrentTime(), y_rqs))
        # self.pvs['x_setcenter'].pv.put(1)
        # self.pvs['y_setcenter'].pv.put(1)
        
    def motorReady_XZTP(self):
        status = self.pvs['xztp_motor_ready'].pv.get(as_string=True)
        ready = 1 if status == 'Ready' else 0
        return ready
        
    def sumMotorDiff(self, motorlist):
        sum_diff = 0
        for m in motorlist:
            sum_diff += abs(self.pvs['%s_Rqs'%m[0]].pv.get() - self.pvs['%s_Act'%m[0]].pv.get())
        return sum_diff
    
    def centerPiezoY(self, waittime = 2, max_ycenter = 31000):
        self.pvs['piezo_yCenter'].pv.put(1)
        self.logger('%s: Piezo ycenter value: %.2f\n'%(getCurrentTime(), self.pvs['y_piezo_val'].pv.get()))
        time.sleep(waittime)

    
    def centerPiezoXY(self):
        MAX_WAIT_TIME = 5  #sec
        self.logger('%s: Centering piezoX and piezoY.\n'%(getCurrentTime()))
        self.pvs['piezo_xCenter'].pv.put(1)
        self.pvs['piezo_yCenter'].pv.put(1)
        self.logger('%s: Piezo xcenter value: %.2f\n'%(getCurrentTime(), self.pvs['x_piezo_val'].pv.get()))
        self.logger('%s: Piezo ycenter value: %.2f\n'%(getCurrentTime(), self.pvs['y_piezo_val'].pv.get()))
        tin = time.time()
        t_diff = 0
        while (not self.motorReady_XZTP()) & (t_diff < MAX_WAIT_TIME):
            self.logger('%s: Waiting for XZTPX to be ready.\n'%(getCurrentTime()))
            t_diff = time.time() - tin
            time.sleep(0.2)
        
        return self.motorReady_XZTP()
    
    def getYCenterValue(self):
        return self.pvs['y_piezo_val'].pv.get()
        
        # MAX_WAIT_TIME = 2  #sec
        # t_diff = 0
        # tin = time.time()
        
        # while (self.pvs['xztp_motor_ready'].pv.get(as_string=True) != 'Ready') & (t_diff < MAX_WAIT_TIME):
        #     self.logger('%s: Waiting for piezoX.\n'%(getCurrentTime()))
        #     time.sleep(0.2)
        #     t_diff = time.time() - tin
        # x_status = 1 if self.pvs['xztp_motor_ready'].pv.get(as_string=True) == 'Ready' else 0
        # print(x_status)
            
        # self.pvs['piezo_yCenter'].pv.put(1)
        # t_diff = 0
        # tin = time.time()
        # while (self.pvs['y_motor_ready'].pv.get(as_string=True) != 'Ready') & (t_diff < MAX_WAIT_TIME):
        #     self.logger('%s: Waiting for piezoY.\n'%(getCurrentTime()))
        #     time.sleep(0.2)
        #     t_diff = time.time() - tin
        # y_status = 1 if self.pvs['y_motor_ready'].pv.get(as_string=True) == 'Ready' else 0
        # print(y_status)
        
        # return x_status * y_status

    
    def assignPosValToPVs(self, pvstr, pvval):
        for s_, v_ in zip(pvstr, pvval):
            self.pvs[s_].pv.put(v_)
            self.logger('%s: Change %s to %.3f\n' % (getCurrentTime(), s_, v_))
    
    def assignEng(self, pvstr, pvval):
        self.pvs[pvstr].pv.put(pvval)
        self.logger('%s: Change %s to %.3f\n' % (getCurrentTime(), pvstr, pvval))
        
    def assignSinglePV(self, pvstr, pvval):
        # previous logic at bnp
        # self.pvs[pvstr].pv.put(pvval)
        # self.logger('%s: Change %s to %.3f\n' % (getCurrentTime(), pvstr, pvval))
        
        # current logic at 2idd, checking y-center value on sm_y
        if 'y' in pvstr:
            self.centerPiezoY()
        self.pvs[pvstr].pv.put(pvval)
        self.logger('%s: Change %s to %.3f\n' % (getCurrentTime(), pvstr, pvval))
            
    def writeScanInit(self, mode, smpinfo, scandic):
        next_sc = self.nextScanName()   #next scan name 'xxx.mda' from pvs
        self.logger('%s Initiating scan %s %s\n'%('#'*20, next_sc, '#'*20)) #log: ######Initiating scan num########
        self.logger('Sample info: %s\n'% smpinfo)
        self.logger('%s: Setting up scan using %s mode.\n'%(getCurrentTime(), mode))
        self.logger('%s: %s'%(getCurrentTime(), scandic))
        self.logger('\n\n')
        
    def motorReady(self, l, mt):
        self.logger('%s: Checking whether motors are ready.\n'%(getCurrentTime()))
        actpv = self.pvs['%s_Act'%l].pv
        rqspv = self.pvs['%s_Rqs'%l].pv
        self.pvs['%s_Act'%l].motorReady(rqspv, mt)
        
        if self.pvs['%s_Act'%l].motor_ready:
            self.logger('%s: %s motor is in position with value'\
                            '%.2f\n'%(getCurrentTime(), l, actpv.value))
            return 1
        else:
            self.logger('%s: %s motor not in position, current: %.2f,'\
                            ' request: %.2f\n'%(getCurrentTime(), l, actpv.value, rqspv.value))
            return 0     
    
    def nextScanName(self):  #return the name from pvs['basename] and pvs['nextsc']
        return '%s%s.mda'%(self.pvs['basename'].pv.value, 
                           str(self.pvs['nextsc'].pv.value).zfill(4))
    
    def getXYZcenter(self):
        return [np.round(self.pvs[i].pv.value, 2) for i in ['x_center_Act', \
                'y_center_Act', 'z_value_Act']]
        

#-------------------------just to run cur_dir2------------------------------
class pvCommsubclass():
    def __init__(self):
        pass
    def user_folder(self):
        #self.rootfolder = caget('9idbBNP:saveData_fileSystem')  #root till cycle
        self.rootfolder = r'/mnt/micdata1/bnp/2023-1'
        #self.rootfolder = self.rootfolder.replace('//micdata/data1','/mnt/micdata1')
        #self.user = caget('9idbBNP:saveData_subDir').split('/')[0]  #user and mda
        self.user ='test_xy9'
        self.user_folder = os.path.join(self.rootfolder,self.user,'Coarse_images')
        return self.user_folder
    def scan_mda(self):
        #self.scanmda = caget('9idbBNP:saveData_fileName')
        self.scan1 = 'bnp_fly0001'
        #self.scan1 = self.scanmda.split('.')[0]
        return self.scan1
    def user_di(self):
        #self.rootfolder = caget('9idbBNP:saveData_fileSystem')  #root till cycle
        self.rootfolder = r'/mnt/micdata1/bnp/2023-1'	
        #self.rootfolder = self.rootfolder.replace('//micdata/data1','/mnt/micdata1')
        self.user ='test_xy9'
        #self.user = caget('9idbBNP:saveData_subDir').split('/')[0]  #user and mda
        self.user_f = os.path.join(self.rootfolder,self.user)
        return self.user_f
    def user__fine_folder(self):
        #self.rootfolder = caget('9idbBNP:saveData_fileSystem')  #root till cycle
        self.rootfolder = r'/mnt/micdata1/bnp/2023-1'
        #self.rootfolder = self.rootfolder.replace('//micdata/data1','/mnt/micdata1')
        #self.user = caget('9idbBNP:saveData_subDir').split('/')[0]  #user and mda
        self.user ='test_xy9'
        self.user_fine_folder = os.path.join(self.rootfolder,self.user,'Fine_images')
        return self.user_fine_folder
    def user_h5_folder(self):
        #self.rootfolder = caget('9idbBNP:saveData_fileSystem')  #root till cycle
        self.rootfolder = r'/mnt/micdata1/bnp/2023-1'
        #self.rootfolder = self.rootfolder.replace('//micdata/data1','/mnt/micdata1')
        self.user ='test_xy9'        
	#self.user = caget('9idbBNP:saveData_subDir').split('/')[0]  #user and mda
        self.user_h5_folder= os.path.join(self.rootfolder,self.user,'img.dat')
        return self.user_h5_folder
    def next_scan_num(self):
        self.next_scan = 1 #caget('9idbBNP:saveData_scanNumber')   #next scan read from PV
        return self.next_scan
        
