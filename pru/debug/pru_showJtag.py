from mmap import mmap
import time, struct
import os

def getbit(val):
	if val:
		return 1
	return 0

def get8(offset):
	offset += pru_dataram
	return int(struct.unpack("<B",mem[offset])[0])

def get16(offset):
	offset += pru_dataram
	return int(struct.unpack("<L",mem[offset:offset+4])[0] & 0xFF)

def get32(offset):
	offset += pru_dataram
	return int(struct.unpack("<L",mem[offset:offset+4])[0])

pru_offset = 0x4a300000
pru_size = 0x4a3244FF - pru_offset
print "Openning pru memory"
mem = None
with open("/dev/mem", "r+b" ) as f:
	mem = mmap(f.fileno(), pru_size, offset=pru_offset)

pru0_dataram = 0x0
pru1_dataram = 0x2000
pru_dataram = pru0_dataram

readfuncs = {
	1:get8,
	2:get16,
	4:get32
}

dataaddresses = [
	# format is name, (num bytes, offset)
	("heartbeat",(1,0x18)),
	
	("startTransaction",(4,0x0)),
	("startTransaction.type",(1,0x0)),
	("startTransaction.subtype",(1,0x1)),
	("startTransaction.flags",(2,0x2)),
	
	("result",(4,0xC)),
	
	("transactionComplete",(1,0x14)),
	("transactionError_addr	", (2,0x16)),
	("transactionCount",(4,0x1c)),
	("transactionInvalid",(4,0x20)),
	("transactionReadCount",(4,0x24)),
	("transactionWriteCount",(4,0x28)),
	("transactionInvalidType",(4,0x34)),
	
	("debug_addr",(4,0x30)),

	("longs[0]",(4,0x04)),
	("longs[1]",(4,0x08)),
]

try:
	# while True:
		# regvals = []
		# for offset in range(4):
			# pos = pru_dataram + offset*4
			# val = get32(pos)
			# regvals.append(hex(val))
		# time.sleep(1)
		# print regvals
		# break
	print "\x1b[2J\n" # clear the screen
	cnt = 0
	while True: 
		print "\x1b[H\n"  # move the cursor to the top
		lines = ["********"]
		append = lines.append
		for entry in dataaddresses:
			name, data = entry
			bytes,offset = data
			value = int(readfuncs[bytes](offset))
			if name == "phyid":
				append("  phyid = %d" % (value & 0x1))
				append("  port = %d" % (value >> 5))
			else:
				append("  %s = %d" % (name, value))
		print "         \n".join(lines)
		time.sleep(0.5)
		data = []
		# print "\n"*20
		# for o in range(0x100,0x500):
			# data.append(get8(o))
		# print ",".join(map(str,data))
		# exit(1)
			

finally:
	mem.close()
	print "EXITING"
