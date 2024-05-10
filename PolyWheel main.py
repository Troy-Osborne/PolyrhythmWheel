from PIL import Image,ImageDraw
from struct import unpack,pack
from math import pi,cos,sin
import wave
from matplotlib import pyplot as plt
Framerate=44100
Videorate=60
loop_seconds=59
frame=0
stepsize=1/(44100*loop_seconds)*pi*2
tau=2*pi
H=1980##Resolution Height
W=(H*9)//16   ##Resolution Width (Currently set to 9/16ths of Height
HH=H//2
HW=W//2

def BlipEnv(N,Length=3000):
    A=int(44100/1000*15)
    R=int(44100/1000*(Length/N-15))
    o=[]
    for i in range(A):#15 milliseconds
        o.append(i/A)
    for i in range(R):
        o.append(1-i/R)
    return o

##Make 4 Octaves of the natural minor scale
Nums=[]
for octaves in range(4):
        Nums+=[0+octaves*12,1+octaves*12,4+octaves*12,5+octaves*12,7+octaves*12,8+octaves*12,10+octaves*12]
        ##Set to [0+octaves*12,2+octaves*12,3+octaves*12,5+octaves*12,7+octaves*12,8+octaves*12,10+octaves*12] for Minor Scale
        ##Change This to [0+octaves*12,2+octaves*12,4+octaves*12,5+octaves*12,7+octaves*12,9+octaves*12,11+octaves*12] for the Major Scale
        ##Change This to [0+octaves*12,1+octaves*12,4+octaves*12,5+octaves*12,7+octaves*12,8+octaves*12,10+octaves*12] for the Phrygian Dominant
#Nums=[1,2,3,5,7,11,13,17,19,23,29,31,37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]  ##Set Nums as prime numbers and 1
def Blip(n):
    freq=440*2**((Nums[n]-49+28)/12)###By Default everything will be tuned to 0= A0 you'll have to add the semitones after -49 to change it
    #e.g. 440*2**((Nums[n]-49+2)/12) would tune it to B or 440*2**((Nums[n]-49+3)/12) to C
    env=BlipEnv(n)
    return [int((sin(freq/44100*i*tau)*env[i]/(1+n**.7))*2**14) for i in range(len(env))]
def NaturalHarmonic(N,BaseFreq=98):
    freq=BaseFreq*(1+N)
    env=BlipEnv(N+1,Length=4000)
    return [int((sin(freq/44100*i*tau)*env[i]/(1+N))*2**15) for i in range(len(env))]
    

#Construct 27 Blips, each one with a frequency depending on the Nums list (by default set to Natural Minor Scale
Blips=[NaturalHarmonic(i) for i in range(0,100)]


class wheel:
    def __init__(self,Sounds,Rates,Phaseshifts=None):
        if Phaseshifts==None:
            self.Pos=[tau-pi/2 for i in Chord]
        else:
            self.Pos=Phaseshifts
            
        self.Sounds=Sounds
        self.Rates=Rates
    def run(self,Loops=1):
        Dir="./Frames/"
        notes=[]
        First=False
        for i in range(len(self.Pos)):
            if self.Pos[i]==0 or self.Pos[i]==tau:
                notes.append((0,self.Sounds[i]))
                self.Pos[i]=0
        frame=0
        for step in range(int(Framerate*loop_seconds)*Loops):
            self.Pos=list(map(lambda a,b:a*stepsize+b,self.Rates,self.Pos))
            curpos=int(step/Framerate*Videorate)
            for i in range(len(self.Pos)):
                    if self.Pos[i]>tau:
                        notes.append((step,self.Sounds[i]))
                        self.Pos[i]-=tau
            if curpos>frame or First==False:
                
                frame=int(step/Framerate*Videorate)
                #check if pos > 2pi if it is set back by 2pi and play sound
                im=Image.new("RGB",(W,H),(0,0,0))
                dr=ImageDraw.Draw(im)
                dr.line((HW,HH,W,HH),fill=(128,128,128),width=10)
                for i in range(len(self.Pos)):
                    x,y=HW+cos(self.Pos[i])*HW/80*(i+3),HH+sin(self.Pos[i])*HW/80*(i+3)
                    dr.ellipse((x-20,y-20,x+20,y+20),fill=(i*26,int(128+sin(step/44100*pi)*126),255-i*26))
                First=True
                im.save(Dir+"Phyr%04d.png"%frame)
        return notes

def loadsound(filename):
    
    out=[]
    f=wave.open(filename)
    channels=f.getnchannels()
    while 1:
        val=f.readframes(1)
        if val:
            val=unpack("hh",val)
            out.append(val[0])
        else:
            break
    del f
    return out

###Put the filenames of your input files here
Inputs=["C:/Users/User/Desktop/Poly/Samples/Kick.wav",
"C:/Users/User/Desktop/Poly/Samples/Snare.wav",
"C:/Users/User/Desktop/Poly/Samples/B High.wav",
"C:/Users/User/Desktop/Poly/Samples/Bass B1.wav",
"C:/Users/User/Desktop/Poly/Samples/Bass C1.wav",
"C:/Users/User/Desktop/Poly/Samples/Bass C2.wav",
"C:/Users/User/Desktop/Poly/Samples/Bass G.wav",
"C:/Users/User/Desktop/Poly/Samples/BellB4.wav",
"C:/Users/User/Desktop/Poly/Samples/BellC4.wav",
"C:/Users/User/Desktop/Poly/Samples/BellC5.wav",
]

Inputs=[]

MySounds=[loadsound(i) for i in Inputs]

Sounds=MySounds+Blips
#Chord=[0,0,1,1]
Chord=list(range(1,100))
#Chord.reverse()
Rates=list(range(1,100))
#Rates.reverse()
Phaseshifts=[0 for i in Rates]
test=wheel(Chord,Rates,Phaseshifts)


def savesound(l):
    f=wave.open("new.wav","w")
    f.setframerate(44100)
    f.setnchannels(2)
    f.setsampwidth(2)
    for val in l:
        val=-32768 if val<-32768  else val
        val=32767 if val>32767  else val
        f.writeframes(pack("h",val))
        f.writeframes(pack("h",val))
    return f
        

def makefile(Sounds,Notes,Loops):
    Length=int(Framerate*loop_seconds)*Loops
    N=[0 for i in range(Length)]
    for note in Notes:
        pos,sound=note
        sound=Sounds[sound]
        for val in sound:
            if pos<len(N):
                N[pos]+=val
                pos+=1
            else:
                break
    return N
notes=test.run(Loops=1)
sound=makefile(Sounds,notes,Loops=1)
#from matplotlib import pyplot as plt
#plt.plot(sound)
#plt.show()

f=savesound(sound)
