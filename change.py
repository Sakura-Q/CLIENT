TX_BUFSIZE=150				
RX_BUFSIZE=5000				

bSerialTXBuff=['0']*100
#bSerialRXBuff[RX_BUFSIZE]=[0]
#将用ASCII表示的十六进制数，转换为真实的数据
def ASCIIToHex(RXBuff, wStartAddr, bCount):
    wHex=0
    for i in range(bCount):
        bTemp=ord(RXBuff[wStartAddr+i])
        if bTemp<58:
            wHex=wHex*16+bTemp-48
        else:
            wHex=wHex*16+bTemp-55
        
    return wHex
    
bASCIITemp = [0, 0]
def ByteToASCII(bByte):
    ASCIITemp=int(bByte/16)
    if ASCIITemp>9:
        bASCIITemp[0]=ASCIITemp+55		
    else:
        bASCIITemp[0]=ASCIITemp+48
    ASCIITemp=bByte%16
    if ASCIITemp>9:
        bASCIITemp[1]=ASCIITemp+55
    else:
        bASCIITemp[1]=ASCIITemp+48
        
bNetworkPortType=0 
wCommReadDataStartAddr=0
wCommReadDataCount=0
wDataRam=[0]*100
wRunState1=0
wRunState2=0
wFaultState=0
def DateProcess(sever_recbuf):
    bCommFCS = 0
    index=0
    wDataLen=0
    for index in range(len(sever_recbuf)):
        if '*'==sever_recbuf[index]:
            break
    wDataLen=index
    case=sever_recbuf[3]
    if case=='1':
            bNetworkPortType=1
            wCommReadDataStartAddr = ASCIIToHex( sever_recbuf, 10, 2 )
            wDataRam[wCommReadDataStartAddr]=ASCIIToHex(sever_recbuf, 12, 4)
    elif case=='2':
            bNetworkPortType=2
            wCommReadDataStartAddr = ASCIIToHex( sever_recbuf, 10, 2 )
            wDataRam[wCommReadDataStartAddr]=ASCIIToHex(sever_recbuf, 12, 4)
    elif case=='3':
            bNetworkPortType=3
            wRunState1=ASCIIToHex(sever_recbuf,10,4)
            wRunState2 = ASCIIToHex(sever_recbuf, 14, 4)
            wFaultState = ASCIIToHex(sever_recbuf, 18, 4)
    elif case=='4':
            bNetworkPortType=4
            wRunState1 = ASCIIToHex(sever_recbuf, 10, 4)
            wRunState2 = ASCIIToHex(sever_recbuf, 14, 4)
            wFaultState = ASCIIToHex(sever_recbuf, 18, 4)
    elif case=='5':
            bNetworkPortType=5
            wCommReadDataStartAddr=ASCIIToHex(sever_recbuf, 4, 2 )
            print(wCommReadDataStartAddr)
            wCommReadDataCount =int((wDataLen-4)/2)
            print(wCommReadDataCount)
            for i in range(wCommReadDataCount):
                wDataRam[wCommReadDataStartAddr+i]=ASCIIToHex( sever_recbuf, i*2+4, 2)
    elif case=='6':
            bNetworkPortType=6
            wCommReadDataStartAddr = ASCIIToHex(sever_recbuf, 10, 2)
            wDataRam[wCommReadDataStartAddr] = ASCIIToHex(sever_recbuf, 12, 2)
    elif case=='7':
            bNetworkPortType=9
    elif case=='8':
            bNetworkPortType=8
            


wCommTXDataAddr=0           
def DataProduce(bCommType, wCommReadDataStartAddr, wCommChangeDateStartCount):  
      bCommmFCS=0
      # del bSerialTXBuff[:]
      bSerialTXBuff[0]='@'
      bSerialTXBuff[1]='0'
      bSerialTXBuff[2]='0'
      if 1==bCommType:
          bSerialTXBuff[3]='1'
      elif 2==bCommType:
          bSerialTXBuff[3]='2'
      elif 2==bCommType:
          bSerialTXBuff[3]='2'
      elif 3==bCommType:
          bSerialTXBuff[3]='3'
      elif 4==bCommType:
          bSerialTXBuff[3]='4'
      elif 5==bCommType:
          bSerialTXBuff[3]='5' 
      elif 6==bCommType:
          bSerialTXBuff[3]='6'
      elif 8==bCommType:
          bSerialTXBuff[3]='8'
          
      if 1==bCommType:
           ByteToASCII(wCommReadDataStartAddr)
           for i in range(2):
               bSerialTXBuff[4+i]=bASCIITemp[i]
           wCommTXDataAddr=6
           
      elif 2==bCommType:
           ByteToASCII(wCommReadDataStartAddr)
           for i in range(2):
               bSerialTXBuff[4+i]=bASCIITemp[i]
           ByteToASCII(wDataRam[wCommReadDataStartAddr]//256)
           for i in range(2):
               bSerialTXBuff[6+i]=bASCIITemp[i]
           ByteToASCII(wDataRam[wCommReadDataStartAddr]%256)
           for i in range(2):
               bSerialTXBuff[8+i]=bASCIITemp[i]
           wCommTXDataAddr=10
           
      elif 4==bCommType:
          wCommTXDataAddr=4
          
      elif 5==bCommType:
           ByteToASCII(wCommReadDataStartAddr)
           for i in range(2): 
               bSerialTXBuff[4+i]=chr(bASCIITemp[i])
           wCommTXDataAddr=6
           ByteToASCII(wCommChangeDateStartCount)
           for i in range(2): 
               bSerialTXBuff[6+i]=chr(bASCIITemp[i])
           wCommTXDataAddr=8

      elif 6==bCommType:
           ByteToASCII(wCommReadDataStartAddr)
           for i in range(2): 
               bSerialTXBuff[4+i]=chr(bASCIITemp[i])
           wCommTXDataAddr=6
           for i in range(wCommChangeDateStartCount):
               ByteToASCII(wDataRam[wCommReadDataStartAddr+i]//256)
               for j in range(2):
                   bSerialTXBuff[wCommTXDataAddr + j] = chr(bASCIITemp[j])
               wCommTXDataAddr=wCommTXDataAddr+2
               ByteToASCII(wDataRam[wCommReadDataStartAddr+i]%256)
               for z in range(2):
                   bSerialTXBuff[wCommTXDataAddr + z] = chr(bASCIITemp[z])
               wCommTXDataAddr = wCommTXDataAddr + 2

      elif 8==bCommType:
          if wCommReadDataStartAddr==1:
              bSerialTXBuff[4]='Y'
          elif wCommReadDataStartAddr==0:
              bSerialTXBuff[4]='N'
          wCommTXDataAddr=5

      for i in range(wCommTXDataAddr):
          bCommmFCS=(bCommmFCS)^ord(bSerialTXBuff[i])

      # bCommmFCS=3

      ByteToASCII(bCommmFCS)
      for i in range(2):
          bSerialTXBuff[wCommTXDataAddr + i] = chr(bASCIITemp[i])
      wCommTXDataAddr=wCommTXDataAddr+2
      bSerialTXBuff[wCommTXDataAddr]='*'
      wCommTXDataLength=wCommTXDataAddr


      
      

if __name__ == '__main__':

    ex=['4','0']
    st=ASCIIToHex(ex, 0, 2)
    ByteToASCII(st)
    print(bASCIITemp[0], bASCIITemp[1])
    print (ASCIIToHex(ex, 0, 2))
    wDataRam[15]=8000
    wDataRam[16]=9000
    DataProduce(6,12,5)
    print(bSerialTXBuff)
    DateProcess(bSerialTXBuff)
    print(wDataRam)
    
    
