##########################################################
#	atr_decoder.py 
#		Author 	: Bondhan Novandy
#		Date	: 12-13 May 2011
#
#		License	: Creative Commons Attribution-ShareAlike 3.0 Unported License.
#				  http://creativecommons.org/licenses/by-sa/3.0/
#		Publish	: http://bondhan.web.id (For education purpose only)
#		Version	: 0.9b
#
#		Fixes	: 13 May 2011, Initial release
#				  13 May 2011 @21:14, fix bug when no argv
#				  23 June 2011 @11.35, fix when detected T = 15
#
##########################################################

import sys
import re

# Constants
ATR_ERR_MSG = {}
ATR_ERR_MSG[0x500] = 'ATR is invalid, the length is not even!'
ATR_ERR_MSG[0x501] = 'ATR is invalid. Unknown chars found!'
ATR_ERR_MSG[0x502] = 'TS is unknown'
ATR_ERR_MSG[0x503] = 'Incomplete ATR'
ATR_ERR_MSG[0x504] = 'ATR size is more than 32 bytes'

def pause():
	raw_input('press Enter to continue..')
	
# Calculate the ETU
def calcEtu(FI, DI):
	
	F = 372
	D = 1
	
	FId = int(FI, 16)
	DId = int(DI, 16)
	
	if FId == 0x00:
		F = 372
	elif FId == 0x01:
		F = 372
	elif FId == 0x02:
		F = 558
	elif FId == 0x03:
		F = 744	
	elif FId == 0x04:
		F = 1116	
	elif FId == 0x05:
		F = 1488	
	elif FId == 0x06:
		F = 1860	
	elif FId == 0x07:
		F = 372		# RFU
	elif FId == 0x08:
		F = 372		# RFU
	elif FId == 0x09:
		F = 512
	elif FId == 0x0A:
		F = 768	
	elif FId == 0x0B:
		F = 1024
	elif FId == 0x0C:
		F = 1536
	elif FId == 0x0D:
		F = 2048	
	elif FId == 0x0E:
		F = 372		# RFU	
	elif FId == 0x0F:
		F = 372		# RFU
	else:
		F = 372
			
	if DId == 0x00:
		D = 1
	elif DId == 0x01:
		D = 1
	elif DId == 0x02:
		D = 2
	elif DId == 0x03:
		D = 4	
	elif DId == 0x04:
		D = 8	
	elif DId == 0x05:
		D = 16	
	elif DId == 0x06:
		D = 32	
	elif DId == 0x07:
		D = 1		# RFU
	elif DId == 0x08:
		D = 12
	elif DId == 0x09:
		D = 20
	elif DId == 0x0A:
		D = 1		# RFU
	elif DId == 0x0B:
		D = 1	# RFU
	elif DId == 0x0C:
		D = 1	# RFU
	elif DId == 0x0D:
		D = 1	# RFU
	elif DId == 0x0E:
		D = 1	# RFU
	elif DId == 0x0F:
		D = 1		# RFU
	else:
		D = 1
	
	return (F/D)
			
	
# Function to decode the ATR
def decode_atr(atr):
	# global
	hist_num = 0
	T_PROT = 0
	TC1_ETU = 0
	TA1 = -1
	TB1 = -1
	TC1 = -1
	TD1 = -1
	TA2 = -1
	TB2 = -1
	TC2 = -1
	TD2 = -1
	TA3 = -1
	TB3 = -1
	TC3 = -1
	TD3 = -1
	
	# Assume that there's no error
	ret = 0
	
	atr_seq = ''.join(atr)		# Join the list again as full string
	
	#############################
	# Cek if ATR is valid
	#############################
	print '____________________ATR____________________'
	print 'ATR	= '+atr_seq.upper()+' (length = '+str(len(atr_seq)/2)+' Dec)'
	
	# if contains besides alphabet or numbers
	pattern = '[^a-fA-F0-9]'
	
	# Cek if the length is even
	if (len(atr_seq) % 2) != 0:
		return ATR_ERR_MSG[0x500]
	elif len(re.findall(pattern, atr_seq)) != 0:
		return ATR_ERR_MSG[0x501]
	elif (len(atr_seq)/2) > 32:
		return ATR_ERR_MSG[0x504]
	
	#############################
	# TS
	#############################
	byte = 0
	
	if byte+2 > len(atr_seq):
		return ATR_ERR_MSG[0x503]
	
	two_chars = (atr_seq[byte:(byte+2)]).upper()
	
	if two_chars == '3B':
		out_str = 'Direct Convention'
	elif two_chars == '3F':
		out_str = 'Inverse Convention'
	else:
		return ATR_ERR_MSG[0x502]
		
	print
	print 'TS	= '+two_chars
	print '		-> '+out_str
	
	#############################
	# T0	
	#############################
	byte += 2
	
	if byte+2 > len(atr_seq):
		return ATR_ERR_MSG[0x503]	
	
	MSB = (atr_seq[byte:(byte+1)]).upper()
	LSB = (atr_seq[(byte+1):(byte+2)]).upper()
	
	print 'T0	= '+MSB+LSB	
	
	# History bytes
	hist_num = int(str(LSB), 16)
	
	print '		-> '+str(hist_num)+' historical characters'
	
	if int(MSB, 16) & 0x01:
		TA1 = 0
		print '		-> TA1 exists'
	if int(MSB, 16) & 0x02:
		TB1 = 0
		print '		-> TB1 exists'
	if int(MSB, 16) & 0x04:
		TC1 = 0
		print '		-> TC1 exists'
	if int(MSB, 16) & 0x08:
		TD1 = 0
		print '		-> TD1 exists'
	
	#############################
	# TA1	
	#############################
	if TA1 > -1:
		
		byte += 2		
		
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]
		
		FI = (atr_seq[byte:(byte+1)]).upper()
		DI = (atr_seq[(byte+1):(byte+2)]).upper()
		
		print 'TA1	= ' + FI+DI
		
		ETU = calcEtu(FI, DI)
		
		print '		-> FI = 0x'+FI+' ('+bin(int(str(FI),16))+')'
		print '		-> DI = 0x'+DI+' ('+bin(int(str(DI),16))+')'
		print '		-> F/D = '+str(ETU)
		
	#############################
	# TB1	
	#############################
	if TB1 > -1:
		
		byte += 2
		
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]
		
		MSB = (atr_seq[byte:(byte+1)]).upper()
		LSB = (atr_seq[(byte+1):(byte+2)]).upper()
		BOTH = str(MSB+LSB)

		II = (int(MSB) >> 2)
		PI1 = (int(BOTH,16)) & 0b00111111
		
		print 'TB1	= '+BOTH
		
		print '		-> II	= '+str(II)
		print '		-> PI1	= '+str(PI1)
			
	
	#############################
	# TC1	
	#############################
	if TC1 > -1:
	
		byte += 2

		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]

		BOTH = (atr_seq[byte:byte+2]).upper()
		
		TC1_ETU = int(str(BOTH), 16)
		
		print 'TC1	= '+BOTH		
				
	#############################
	# TD1	
	#############################	
	if TD1 > -1:
		byte += 2
		
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]

		MSB = (atr_seq[byte:(byte+1)]).upper()
		LSB = (atr_seq[(byte+1):(byte+2)]).upper()
	
		print 'TD1	= '+MSB+LSB
		
		print '		-> Protocol T = '+ str(int(LSB,15))
		
		T_PROT = int(LSB, 16)
		
		if TC1 > -1:
			if T_PROT == 0 and TC1_ETU == 255:
				print '		-> guard time (from TC1) = 2 etu'
			elif T_PROT == 1 and TC1_ETU == 255:
				print '		-> guard time (from TC1) = 1 etu'
			else:
				print '		-> guard time (from TC1) = ' + str(TC1_ETU) + ' etu'
					
		if int(MSB, 16) & 0x01:
			TA2 = 0
			print '		-> TA2 exists'
		if int(MSB, 16) & 0x02:
			TB2 = 0
			print '		-> TB2 exists'
		if int(MSB, 16) & 0x04:
			TC2 = 0
			print '		-> TC2 exists'
		if int(MSB, 16) & 0x08:
			TD2 = 0
			print '		-> TD2 exists'
	
		#This rule below is probably wrong
		#if T_PROT == 1:
		#	if (TC1 & 0x01) == 0x00:
		#		print '		-> LRC is used (from TC1)'
		#	elif (TC1 & 0x01) == 0x01:
		#		print '		-> CRC is used (from TC1)'

	#############################
	# TA2	
	#############################	
	if TA2 > -1:
		byte +=2
		
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]

		MSB = (atr_seq[byte:(byte+1)]).upper()
		LSB = (atr_seq[(byte+1):(byte+2)]).upper()

		print 'TA2	= '+MSB+LSB
		print '		-> Protocol T = '+str(int(LSB,16))
		
		if (int(MSB,16) & 0b1000) > 0:
			print '		-> Not Negotiable'
		else:
			print '		-> Negotiable'
		
		
	#############################
	# TB2	
	#############################	
	if TB2 > -1:
		byte +=2	
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]	

		MSB = (atr_seq[byte:(byte+1)]).upper()
		LSB = (atr_seq[(byte+1):(byte+2)]).upper()
		print 'TB2	= '+MSB+LSB			
	

	#############################
	# TC2	
	#############################	
	if TC2 > -1:
		byte +=2
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]
		
		if T_PROT == 0:
			print '		-> WI = '+str(T_PROT)

		MSB = (atr_seq[byte:(byte+1)]).upper()
		LSB = (atr_seq[(byte+1):(byte+2)]).upper()
		print 'TC2	= '+MSB+LSB
			
	#############################
	# TD2	
	#############################	
	if TD2 > -1:
		byte +=2
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]

		MSB = (atr_seq[byte:(byte+1)]).upper()
		LSB = (atr_seq[(byte+1):(byte+2)]).upper()
		
		print 'TD2	= '+MSB+LSB
		print '		-> T = '+ str(int(LSB, 16))
		
		# rewrite T_PROT
		T_PROT = int(LSB, 16)

		if int(MSB, 16) & 0x01:
			TA3 = 0
			print '		-> TA3 exists'
		if int(MSB, 16) & 0x02:
			TB3 = 0
			print '		-> TB3 exists'
		if int(MSB, 16) & 0x04:
			TC3 = 0
			print '		-> TC3 exists'
		if int(MSB, 16) & 0x08:
			TD3 = 0
			print '		-> TD3 exists'

			
	#############################
	# TA3	
	#############################	
	if TA3 > -1:
		byte +=2
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]

		MSB = (atr_seq[byte:(byte+1)]).upper()
		LSB = (atr_seq[(byte+1):(byte+2)]).upper()
		BOTH = MSB+LSB
		
		print 'TA3	= '+MSB+LSB			
		
		if T_PROT == 1 :
			print '		-> Max Buffer = '+str(int(BOTH,16))+' bytes'
		elif T_PROT == 15:
			XI = (int(MSB, 16) >> 2)
			UI = (int(BOTH,16)) & 0b00111111
			print '		-> XI =	'+str(XI)
			print '		-> UI =	'+str(UI)
		
	#############################
	# TB3	
	#############################	
	if TB3 > -1:
		byte +=2
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]
			
		MSB = (atr_seq[byte:(byte+1)]).upper()
		LSB = (atr_seq[(byte+1):(byte+2)]).upper()
		print 'TB3	= '+MSB+LSB
		
		if T_PROT == 1:
			print '		-> BWI = '+MSB
			print '		-> CWI = '+LSB

	#############################
	# TC3	
	#############################	
	if TC3 > -1:
		byte +=2
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]

		MSB = (atr_seq[byte:(byte+1)]).upper()
		LSB = (atr_seq[(byte+1):(byte+2)]).upper()
		print 'TC3	= '+MSB+LSB
		
		TC3_BYTE = int(MSB+LSB, 16)
		
		if (T_PROT == 0x01):
			if (TC3_BYTE & 0x01) == 0x00:
				print '		-> LRC is used (from TC3)'
			elif (TC3_BYTE & 0x01) == 0x01:
				print '		-> CRC is used (from TC3)'
		
	#############################
	# TD3	
	#############################	
	if TD3 > -1:
		byte +=2
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]

		MSB = (atr_seq[byte:(byte+1)]).upper()
		LSB = (atr_seq[(byte+1):(byte+2)]).upper()
		print 'TD3	= '+MSB+LSB			
		
	############################
	# Historical Bytes	
	#############################	
	byte += 2
	
	if byte + (hist_num*2) > len(atr_seq):
		return ATR_ERR_MSG[0x503]

	hist_ascii = []		
	for i in range (byte, byte+(hist_num*2), 2):
		#print i
		#print 'leng ='+str(len(atr_seq))
		if i >= len(atr_seq):
			break
			
		char = atr_seq[i:i+2]
		#print 'char = '+char
		tmp = int(char,16)
		#print 'ff = '+ str(fff)
		hist_ascii.append(chr(tmp))
			
	print 'T1-TK	= '+atr_seq[byte:(byte+(hist_num*2))] + ' ' 
	print '		-> Means: \''+''.join(hist_ascii)+'\''
	
	
	#############################
	# TCK	
	#############################	
	if T_PROT != 0:
		byte += hist_num*2
		if byte+2 > len(atr_seq):
			return ATR_ERR_MSG[0x503]
		
		MSB = (atr_seq[byte:(byte+1)]).upper()
		LSB = (atr_seq[(byte+1):(byte+2)]).upper()
		BOTH = MSB+LSB
		
		print 'TCK	= '+BOTH
		
		xored = 0
		for i in range (2, len(atr_seq)-2, 2):
			
			var = (atr_seq[i]+atr_seq[i+1])
			xored ^= int(var, 16)
			#print var + '->' + str(xored)
			
		print '		-> Calculated TCK: (Dec) '+str(xored)+' or '+str(hex(xored).replace('0x','').upper())
		
		if xored == int(BOTH,16):
			print '		-> ATR Sequence is valid!'
		else:
			print '		-> ATR Sequence is invalid!'
	

	#############################
	# Error Handling	
	#############################
	byte += 2
	if len(atr_seq) > (byte):
		print 'IGNORED	= '+ atr_seq[byte:len(atr_seq)]
		print '		-> Extra Characters found, Ignored'
	
	
	#############################
	# Others
	#############################
	print
	if TC3 == -1 and T_PROT != 0:
		print '		-> LRC is used (default)'
	
	if T_PROT <= 0 and TD1 < 0:
		print '		-> Protocol T = 0 (default)'
	
	
	return ret	

		
## Main function	
if __name__ == '__main__':
	atr = []
	if len(sys.argv) < 2:
		atr = raw_input('Enter the ATR sequence> ')
		atr = atr.split()
	else:
		atr = sys.argv[1:]

	# Let's decode it
	lRet = decode_atr(atr)
	
	if ( lRet != 0 ):
		print	
		print 'Error Message: '
		print lRet
	
		