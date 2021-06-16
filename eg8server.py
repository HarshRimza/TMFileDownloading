from uuid import uuid1
import os
import sys
import pathlib
import socket
import threading

class Model:
 def __init__(self,*dataStructures):
  self.files=dataStructures[0]
  self.users=dataStructures[1]
  self.usersWithUUIDS=dataStructures[2]
  self.filesWithSemaphores=dataStructures[3]

class RequestProcessor(threading.Thread):
 def __init__(self,socket,model):
  self.socket=socket
  self.model=model
  threading.Thread.__init__(self)
  self.start()


 def sendFilesList(self):
  files=bytes(str(self.model.files),"utf-8")
  self.socket.sendall(bytes(str(len(files)).ljust(1024),"utf-8"))
  self.socket.sendall(bytes(files))
 



 def downloadFile(self):
  toReceive=1024
  dataBytes=b''
  dataBytesLength=0
  while dataBytesLength<toReceive:
   by=self.socket.recv(toReceive-dataBytesLength)
   dataBytes+=by
   dataBytesLength+=len(by)
  downloadFileNameLength=int(dataBytes.decode("utf-8").strip())
  
  toReceive=downloadFileNameLength
  dataBytes=b''
  dataBytesLength=0
  while dataBytesLength<toReceive:
   by=self.socket.recv(toReceive-dataBytesLength)
   dataBytes+=by
   dataBytesLength+=len(by)
  downloadFileName=dataBytes.decode("utf-8").strip()
  
  if downloadFileName not in self.model.files:
   self.socket.sendall(bytes("9".ljust(1024),"utf-8"))
   self.socket.sendall(bytes("incorrect","utf-8"))
   return 
  self.socket.sendall(bytes("7".ljust(1024),"utf-8"))
  self.socket.sendall(bytes("correct","utf-8"))

  toReceive=1024
  dataBytes=b''
  dataBytesLength=0
  while dataBytesLength<toReceive:
   by=self.socket.recv(toReceive-dataBytesLength)
   dataBytes+=by
   dataBytesLength+=len(by)
  decisionLength=int(dataBytes.decode("utf-8").strip())
  
  toReceive=decisionLength
  dataBytes=b''
  dataBytesLength=0
  while dataBytesLength<toReceive:
   by=self.socket.recv(toReceive-dataBytesLength)
   dataBytes+=by
   dataBytesLength+=len(by)
  decision=dataBytes.decode("utf-8").strip()
  if decision=="n":return
  
  semaphore=self.model.filesWithSemaphores[downloadFileName]
  semaphore.acquire()
  downloadFileLength=self.model.files[downloadFileName]
  self.socket.sendall(bytes(str(downloadFileLength).ljust(1024),"utf-8"))
  bufferSize=4096
  dataBytes=b''
  with open(f"store{os.path.sep}{downloadFileName}","rb") as file:
   while True:
    dataBytes=file.read(bufferSize)
    if len(dataBytes)==0: break
    self.socket.sendall(dataBytes)
  semaphore.release()

  

 def run(self):
  toReceive=1024
  dataBytes=b''
  dataBytesLength=0
  while dataBytesLength<toReceive:
   by=self.socket.recv(toReceive-dataBytesLength)
   dataBytes+=by
   dataBytesLength+=len(by)
  userInformationLength=int(dataBytes.decode("utf-8").strip())
  
  toReceive=userInformationLength
  dataBytes=b''
  dataBytesLength=0
  while dataBytesLength<toReceive:
   by=self.socket.recv(toReceive-dataBytesLength)
   dataBytes+=by
   dataBytesLength+=len(by)
  userInformation=eval(dataBytes.decode("utf-8").strip())

  if userInformation not in self.model.users.values() or userInformation[0] in self.model.usersWithUUIDS.values():
   self.socket.sendall(bytes("14".ljust(1024),"utf-8"))
   self.socket.sendall(bytes("('incorrect',)","utf-8"))
   self.socket.close()
   print("Thread Ended Successfully")
   return 

  uuidOfThisUser=uuid1()
  self.model.usersWithUUIDS[uuidOfThisUser]=userInformation[0]
  decision=f"('correct','{uuidOfThisUser}')"
  self.socket.sendall(bytes(str(len(decision)).ljust(1024),"utf-8"))
  self.socket.sendall(bytes(decision,"utf-8"))

  while True:
   toReceive=1024
   dataBytes=b''
   dataBytesLength=0
   while dataBytesLength<toReceive:
    by=self.socket.recv(toReceive-dataBytesLength)
    dataBytes+=by
    dataBytesLength+=len(by)
   requestStringLength=int(dataBytes.decode("utf-8").strip())
    
   toReceive=requestStringLength
   dataBytes=b''
   dataBytesLength=0
   while dataBytesLength<toReceive:
    by=self.socket.recv(toReceive-dataBytesLength)
    dataBytes+=by
    dataBytesLength+=len(by)
   operation,userUUID=eval(dataBytes.decode("utf-8").strip())
   
   if userUUID!=str(uuidOfThisUser):
    self.socket.sendall(bytes("9".ljust(1024),"utf-8"))
    self.socket.sendall(bytes("incorrect","utf-8"))
    break
   
   if operation!="quit" and operation!="exit":
    self.socket.sendall(bytes("7".ljust(1024),"utf-8"))
    self.socket.sendall(bytes("correct","utf-8"))
   else :
    del self.model.usersWithUUIDS[uuidOfThisUser] 
    break

   if operation=="files": self.sendFilesList()
   elif operation=="download file":self.downloadFile()
#while loop ends
  self.socket.close()
  print("Thread Successfully Ended")

#Main Script
serverSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
with open('srv.cfg','r') as srvFile: connectivityTuple=eval(srvFile.read().strip())
serverSocket.bind(connectivityTuple)
serverSocket.listen()

files={}
filesWithSemaphores={}
directories_or_files=os.scandir("store")
for entry in directories_or_files: 
 files[entry.name]=entry.stat().st_size
 filesWithSemaphores[entry.name]=threading.Semaphore(5)


users={}
with open("users.usr","rb") as usersDataFile:
 while True:
  userRecord=usersDataFile.readline().strip()
  if len(userRecord)==0:break
  userRecord=eval(userRecord)
  users[userRecord[0]]=userRecord

usersWithUUIDS={}
model=Model(files,users,usersWithUUIDS,filesWithSemaphores)

while True:
 print("Server is ready to accept request...")
 socket,socketName=serverSocket.accept()

 toReceive=1024
 dataBytes=b''
 dataBytesLength=0
 while dataBytesLength<toReceive:
  by=socket.recv(toReceive-dataBytesLength)
  dataBytes+=by
  dataBytesLength+=len(by)
 decisionLength=int(dataBytes.decode("utf-8").strip()) 
 toReceive=decisionLength
 dataBytes=b''
 dataBytesLength=0
 while dataBytesLength<toReceive:
  by=socket.recv(toReceive-dataBytesLength)
  dataBytes+=by
  dataBytesLength+=len(by)
 clientOrNot=dataBytes.decode("utf-8").strip()
 if clientOrNot=="stop server":break

 RequestProcessor(socket,model)
 print("New Thread has been created in memory")

serverSocket.close()
print("Server Closed")