import os
import sys
import pathlib
import socket

def get_files_list(clientSocket,clientUUID):
 request=f"('files','{clientUUID}')"
 clientSocket.sendall(bytes(str(len(request)).ljust(1024),"utf-8"))
 clientSocket.sendall(bytes(request,"utf-8"))

 toReceive=1024
 dataBytes=b''
 dataBytesLength=0
 while dataBytesLength<toReceive:
  by=clientSocket.recv(toReceive-dataBytesLength)
  dataBytes+=by
  dataBytesLength+=len(by)
 decisionLength=int(dataBytes.decode("utf-8").strip())

 toReceive=decisionLength
 dataBytes=b''
 dataBytesLength=0
 while dataBytesLength<toReceive:
  by=clientSocket.recv(toReceive-dataBytesLength)
  dataBytes+=by
  dataBytesLength+=len(by)
 decision=dataBytes.decode("utf-8").strip()
 if decision=='incorrect':
  print("Sorry, You are not registered");
  clientSocket.close()
  sys.exit()

 toReceive=1024
 dataBytes=b''
 dataBytesLength=0
 while dataBytesLength<toReceive:
  by=clientSocket.recv(toReceive-dataBytesLength)
  dataBytes+=by
  dataBytesLength+=len(by)
 filesListLength=int(dataBytes.decode("utf-8").strip())

 toReceive=filesListLength
 dataBytes=b''
 dataBytesLength=0
 while dataBytesLength<toReceive:
  by=clientSocket.recv(toReceive-dataBytesLength)
  dataBytes+=by
  dataBytesLength+=len(by)
 files=eval(dataBytes.decode("utf-8"))

 print(f'+{"-"*30}+{"-"*17}+')
 print(f'|{"FILE".center(30," ")}|{"SIZE".center(17," ")}|')
 print(f'+{"-"*30}+{"-"*17}+')
 for file,size in files.items():print("|%-30s|%17d|" %(file,size))
 print(f'+{"-"*30}+{"-"*17}+')





def download_file(clientSocket,fileNameToDownload,clientUUID):
 request=f"('download file','{clientUUID}')"
 clientSocket.sendall(bytes(str(len(request)).ljust(1024),"utf-8"))
 clientSocket.sendall(bytes(request,"utf-8"))

 toReceive=1024
 dataBytes=b''
 dataBytesLength=0
 while dataBytesLength<toReceive:
  by=clientSocket.recv(toReceive-dataBytesLength)
  dataBytes+=by
  dataBytesLength+=len(by)
 decisionLength=int(dataBytes.decode("utf-8").strip())

 toReceive=decisionLength
 dataBytes=b''
 dataBytesLength=0
 while dataBytesLength<toReceive:
  by=clientSocket.recv(toReceive-dataBytesLength)
  dataBytes+=by
  dataBytesLength+=len(by)
 decision=dataBytes.decode("utf-8").strip()
 if decision=='incorrect':
  print("Sorry, You are not registered");
  clientSocket.close()
  sys.exit()

 clientSocket.sendall(bytes(str(len(fileNameToDownload)).ljust(1024),"utf-8"))
 clientSocket.sendall(bytes(fileNameToDownload,"utf-8"))

 toReceive=1024
 dataBytes=b'' 
 while len(dataBytes)<toReceive:
  by=clientSocket.recv(toReceive-len(dataBytes))
  dataBytes+=by
 doesFileExistResponseLength=int(dataBytes.decode("utf-8").strip())

 toReceive=doesFileExistResponseLength
 dataBytes=b'' 
 while len(dataBytes)<toReceive:
  by=clientSocket.recv(toReceive-len(dataBytes))
  dataBytes+=by
 fileExistsOrNot=dataBytes.decode("utf-8").strip()

 if fileExistsOrNot=="incorrect": 
  print("Sorry, file does not exists");
  return

 saveOrNot=input("Save Y/N : ")

 if saveOrNot in "Yy":
  clientSocket.sendall(bytes("1".ljust(1024),"utf-8"))
  clientSocket.sendall(bytes("y","utf-8"))
 else:
  print("File downloading has been cancelled")
  clientSocket.sendall(bytes("1".ljust(1024),"utf-8"))
  clientSocket.sendall(bytes("n","utf-8"))
  return 

 toReceive=1024
 dataBytes=b'' 
 while len(dataBytes)<toReceive:
  by=clientSocket.recv(toReceive-len(dataBytes))
  dataBytes+=by
 fileLength=int(dataBytes.decode("utf-8").strip())

 with open(fileNameToDownload,"wb") as downloadFile:
  toReceive=4096
  dataLength=0
  print("Wait a minute your file downloading is about to start.... ")
  while dataLength<fileLength:
   if (fileLength-dataLength)<toReceive:toReceive=fileLength-dataLength
   dataBytes=b''
   while len(dataBytes)<toReceive:
    by=clientSocket.recv(toReceive-len(dataBytes))
    dataBytes+=by
   downloadFile.write(dataBytes)
   dataLength+=toReceive  
   percentage=int((dataLength/fileLength)*100)
   print(f"Downloading : {percentage}%",end=" ",flush=True)
 print()
 print("File has been downloaded. Thank you for downloading.")




# Main Script
username=input("Enter Username : ").strip().lower()
password=input("Enter Password : ").strip()
requestString=f"('{username}','{password}')"

clientSocket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
with open("srv.cfg","r") as srvFile: connectivityTuple=eval(srvFile.read().strip()) 
clientSocket.connect(connectivityTuple)
clientSocket.sendall(bytes("12".ljust(1024),"utf-8"))
clientSocket.sendall(bytes("it is client","utf-8"))
clientSocket.sendall(bytes(str(len(requestString)).ljust(1024),"utf-8"))
clientSocket.sendall(bytes(requestString,"utf-8"))

toReceive=1024
dataBytes=b'' 
while len(dataBytes)<toReceive:
 by=clientSocket.recv(toReceive-len(dataBytes))
 dataBytes+=by
userExistsDecisionLength=int(dataBytes.decode("utf-8").strip())

toReceive=userExistsDecisionLength
dataBytes=b'' 
while len(dataBytes)<toReceive:
 by=clientSocket.recv(toReceive-len(dataBytes))
 dataBytes+=by
userExistsOrNot=eval(dataBytes.decode("utf-8").strip())


if userExistsOrNot[0]=="incorrect": 
 print("Sorry, Your Username/Password is wrong or you have already logged in.");
 clientSocket.close()
 sys.exit()

clientUUID=userExistsOrNot[1]
print()
while True:
 command=input("tmclient>").strip()
 if command=="quit" or command=="exit":
  endConnection=f"('{command}','{clientUUID}')"
  clientSocket.sendall(bytes(str(len(endConnection)).ljust(1024),"utf-8"))
  clientSocket.sendall(bytes(endConnection,"utf-8"))
  break
 elif command=="dir": get_files_list(clientSocket,clientUUID)
 elif command.startswith("get "): download_file(clientSocket,command[4::].strip(),clientUUID)

clientSocket.close()  
print("Bye!") 