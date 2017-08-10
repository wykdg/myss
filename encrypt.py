
from crypto_aes import MyDESCrypt
import struct
class Encrypt:
    def __init__(self):
        self.buf=''
        self.last_len=None
        self.des=MyDESCrypt()
    def encrypt(self,buf):
        # print buf

        if len(buf)==0:
            return buf
        buf=self.des.ecrypt(buf)
        head=struct.pack('i',len(buf))

        return head+buf


    def decrypt(self,buf):
        # print buf

        self.buf+=buf
        data=''
        while True:
            if len(self.buf)==0:
                return data

            if self.last_len is None  :
                if len(self.buf)<4:
                    return data
                self.last_len=struct.unpack('i',self.buf[:4])[0]
                self.buf=self.buf[4:]

            if self.last_len<=len(self.buf):

                slice=self.buf[:self.last_len]
                slice=self.des.decrypt(slice)
                data+=slice
                self.buf=self.buf[self.last_len:]
                self.last_len=None
            else:
                return data


if __name__=='__main__':
    a=Encrypt()
    e=a.encrypt('12345678')+a.encrypt('3112321')
    result=''
    for x in e:
        result+= a.decrypt(x)
    print result