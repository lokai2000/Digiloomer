from PIL import Image
import sys
import pygame
import time
import serial

#Open the imagefile
if len(sys.argv)<2:
  sys.exit ("python {0:s} <image_file>\n\n".format(sys.argv[0]))

try:
  IM = Image.open(sys.argv[1])
except:
  sys.exit("Unable to open {0:s} as image file.\n\n".format(sys.argv[1]))

#Do some conversion if the file needs it
SZX,SZY = IM.size
print "Image File : {0:s}".format(sys.argv[1])
print "X Size     : {0:d}".format(SZX)
print "Y Size     : {0:d}".format(SZY)

IM = IM.convert("1")


size = width, height = 800, 320
black = 0, 0, 0

screen = pygame.display.set_mode(size)

pixOffset = 0

pygame.font.init()
myfont = pygame.font.SysFont("freesansbold.ttf", 24)

statusList  = ["UNCONNECTED", "CONNECTING", "CONNECTED", "WAITING", "STEPPING"]
statusColor = [(255,0,0), (255,255,0), (0,255,0), (64,196,255), (64,196,255)]
statusState = 0

highLightState = 0


def connetTarget():

  ser = serial.Serial("/dev/ttyACM0",9600,timeout=30)
  line = ser.readline()
  if line[0:8] == "DIGILOOM":
    return ser
  else:
    return 0

def sendCmd(IM, pixOffset):
  valA = 0
  for y in range(4):
    pix = IM.getpixel((pixOffset,y))
    if pix:
      valA += 8>>y

  valB = 0
  for y in range(4,8):
    pix = IM.getpixel((pixOffset,y))
    if pix:
      valB += 8>>(y-4)

  #print valA, valB

  ser.write('S')
  ser.write(chr(valA))
  ser.write(chr(valB))

  return

def waitAck():
  line = ser.readline()
  return


ser=0

while 1:
  for event in pygame.event.get():
    if event.type == pygame.QUIT: 
      if ser:
        ser.close()
      sys.exit()
    elif event.type == pygame.KEYDOWN:
      if event.key == pygame.K_ESCAPE:
        if ser:
          ser.close()
        sys.exit()
      if event.key == pygame.K_q:
        if ser:
          ser.close()
        sys.exit()

      #Connect to target
      if event.key == pygame.K_c:
          statusState = 1        

      #Silent move left
      if event.key == pygame.K_COMMA:
        pixOffset -= 1
        pixOffset = max(0,pixOffset)
        highLightState = 0

      #Move left and command
      if event.key == pygame.K_LEFT:
        if statusState==2:
          pixOffset -= 1
          pixOffset = max(0,pixOffset)
          highLightState = 1
          statusState=3
        
      #Silent move right
      if event.key == pygame.K_PERIOD:
        pixOffset += 1
        pixOffset = min(SZX-1,pixOffset)
        highLightState = 0

      #Move right and command
      if event.key == pygame.K_RIGHT:
        if statusState==2:
          pixOffset += 1
          pixOffset = min(SZX-1,pixOffset)
          highLightState = 1
          statusState=3

  screen.fill(black)

  for y in range(SZY):
    for x in range(SZX):
      pix = IM.getpixel((x,y))
      if x==pixOffset:
        screen.fill( (pix/4,pix/2,pix), rect=(x*2,y*2+2,2,2) )
      else:
        screen.fill( (pix,pix,pix), rect=(x*2,y*2+2,2,2) )

  for y in range(SZY):
    for x in range(width/32):
      dispX = pixOffset + x - 12
      if dispX>=0 and dispX<SZX:
        pix = IM.getpixel((dispX,y))
        if x==12:
          if pix:
            screen.fill( (pix/4+(pix/3)*(1-highLightState),highLightState*pix/2,highLightState*pix), rect=(x*32,y*32+22,32,32) )
          else:
            pygame.draw.rect(screen, (32+96*(1-highLightState),highLightState*64,highLightState*128), (x*32,y*32+22,32,32), 1)
        else:
          if pix:
            screen.fill( (pix,pix,pix), rect=(x*32,y*32+22,32,32) )
          else:
            pygame.draw.rect(screen, (64,64,64), (x*32,y*32+22,32,32), 1)

  
  label = myfont.render("STEP: {0:d}".format(pixOffset), 1, (64,196,255))
  screen.blit(label, (378, 290))

  label = myfont.render("STATUS: {0:s}".format(statusList[statusState]), 1, statusColor[statusState])
  screen.blit(label, (16, 290))

  pygame.draw.rect(screen, (64+(191)*(1-highLightState),highLightState*128,highLightState*255), (12*32-6,14,44,270), 3)
  pygame.display.flip()

  if statusState==4:
    waitAck()
    statusState=2

  if statusState==3:
    sendCmd(IM,pixOffset)
    statusState=4

  if statusState==1:
    ser=connetTarget()
    if ser:
      statusState=3
      highLightState=1
    else:
      statusState=0




