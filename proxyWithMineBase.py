import sys
import socket
import threading
from minebase import load_version, load_common_data, Edition # type: ignore
from pprint import pprint  # pretty print (for easier readability)
from collections import defaultdict

"""
proxyWithMineBase builds on the simple proxy I made initally and makes use of the minebase wrapper for the minecraft data library

Still a simple proxy for a minecraft client and server conneciton that takes incoming packets, extracts the packet id
and uses minebase to map the packets id to a name that the user would recognize, such as ID 7 relates to a player chat message.

For this to work the best, the server needs to have a few settings turned off
online-mode=false
enforce-secure-profile=false
network-compression-threshold=-1

Made Reference to these packages, but didn't take any code
https://gitlab.com/cubelib/cubelib 
https://prismarinejs.github.io/minecraft-data/ 
https://gitlab.com/cubelib/MCRP

"""

#Constants
BUF_SIZE = 4096

#Minecraft Version to use with minebase
MC_VERSION = "1.21.6"


def getPacketNames(version_info, state, direction):
    """
    Get all names of packets and associated ID and the direction it goes
    Build a dictionary with {packetId: packetName} for the given state and direction of the packet
    """

    packetDef = version_info["protocol"][state][direction]["types"]["packet"]
    kind, fields = packetDef

    #Find the name field in the packet
    nameField = next(f for f in fields if f["name"] == "name")
    mapper = nameField["type"]
    mappings = mapper[1]["mappings"]

    #Convert hexstring keys from packet's varint to integer
    return {int(k, 16): v for k, v in mappings.items()}


#setup protocol info
version_info = load_version(MC_VERSION, Edition.PC)
Client2Server = getPacketNames(version_info, "play", "toServer")
Server2Client = getPacketNames(version_info, "play", "toClient")

#Create Counters for packet ids
c2sPacketCount = defaultdict(int)
s2cPacketCount = defaultdict(int)

#Chat related packet IDs for 1.21.6 
CHAT_C2S_IDS = {5, 6, 7, 8}
SKIP_BLOCK_PACKETS = 1
BLOCK_PACKETS_READ = 0



def readVarInt(buffer,start = 0):
    """
    Read a varint starting at the start of the buffer 
    Returns the value and bytes used for each var int
    """
    totalRead = 0
    result = 0

    while True:
        if start + totalRead >= len(buffer):
            #Not enough data to read the varint
            return None, 0
    
        byte = buffer[start+totalRead]
        #converts the packets Varint from the buffer into an actual integer we can use to identify the packet
        result |= (byte & 0x7F) << (7 * totalRead)
        totalRead += 1

         #If top bit is 0 then this is the last byte
        if (byte & 0x80) == 0:
            break

        #VarInt in minecraft is always less than 5
        if totalRead > 5:
            raise ValueError("VarInt too big")

    return result, totalRead


def forward(src, dst, direction):
    """
    Contiosuly reads tcp bytes between src and dst. Prints the number of bytes forwrarded
    Runs in its own thread so data traffic can flow in both direcitons simulataneously
    """

    #bring global packet count variables into the function
    global c2sPacketCount,s2cPacketCount,SKIP_BLOCK_PACKETS, BLOCK_PACKETS_READ

    #make a new Byte object to properly store the stream of packets without messing up the stored data 
    packetStreamBuffer = b""

    try:
        while True:
            data = src.recv(BUF_SIZE)
            if not data:
                break 

            #add new tcp data to buffer
            packetStreamBuffer += data

            while True:
                #First, get the packet lengh
                packetLen, lenBytesUsed = readVarInt(packetStreamBuffer, 0)
                if packetLen is None:
                    #Not enough data yet to read the length field
                    break

                totalFrameLen = lenBytesUsed + packetLen

                if len(packetStreamBuffer) < totalFrameLen:
                    #Whole packet isn't in buffer yet
                    break

                #Next slice the packet up into different chunks
                #get the meat of the packet by trimming off the length of the var int section and the length of the packets payload
                wholeFrame = packetStreamBuffer[:totalFrameLen]
                packetContents = wholeFrame[lenBytesUsed:]

                #Next remove the read frame from the buffer
                packetStreamBuffer = packetStreamBuffer[totalFrameLen:]

                #Read next varint inside the packets contents to get packet id
                packetId, idByteLen = readVarInt(packetContents, 0)
                #has to be uncompressed to work


                blocked = False

                #if the packetId is read properly, figure out the direction of the packet, 
                # add 1 to the counter for that type of packet and log the name of it if it hasn't been read yet
                if packetId is not None:
                    if direction == "C->S":
                        c2sPacketCount[packetId] += 1
                        name = Client2Server.get(packetId, "unknown")
                        #Block packets with certain ids relating to chat
                        if packetId in CHAT_C2S_IDS :
                            #have to let join chat message go through otherwise client can never connect
                            if BLOCK_PACKETS_READ >= SKIP_BLOCK_PACKETS:
                                blocked = True
                                print(f"[BLOCKED CHAT] C->S packetId={packetId} ({name})")
                            BLOCK_PACKETS_READ += 1
                    else:
                        s2cPacketCount[packetId] += 1
                        name = Server2Client.get(packetId, "unknown")

                #pprint(f"{direction} packetId={packetId} ({name})")
            
                #finally send the original packet to the other side of the proxy
                if not blocked:
                    dst.sendall(wholeFrame)

          
    except ConnectionResetError:
        pass
    finally:
        try:
            src.close()
        except:
            pass
        try:
            dst.close()
        except:
            pass

         #When the client->server direction ends, print current packet stats
        if direction == "C->S":
            print("\nConnection closed. Packet ID counts so far:")

            print("  (client -> server)")
            for packetid, count in sorted(c2sPacketCount.items()):
                name = Client2Server.get(packetid, "unknown")
                print(f"    ID {packetid:3d} ({name}): {count}")

            print("  (server -> client)")
            for packetid, count in sorted(s2cPacketCount.items()):
                name = Server2Client.get(packetid, "unknown")
                print(f"    ID {packetid:3d} ({name}): {count}")



def handle_client(client_socket, server_host, server_port):
    """
    Used when a new client connects to the proxy
    Creates a conneciton to the real minecraft server
    starts 2 threads
    - one for client - server packets
    - one for server - client packets
    """
    try:
        server_socket = socket.create_connection((server_host, server_port))
    except Exception as e:
        print(f"Error connecting to server: {e}")
        client_socket.close()
        return

    #start threads to forward in both directions and display direciton
    threading.Thread(
        target=forward, args=(client_socket, server_socket, "C->S"), daemon=True
    ).start()
    threading.Thread(
        target=forward, args=(server_socket, client_socket, "S->C"), daemon=True
    ).start()

def main():
    if len(sys.argv) != 5:
        sys.exit(1)

    listen_host = sys.argv[1]
    listen_port = int(sys.argv[2])
    server_host = sys.argv[3]
    server_port = int(sys.argv[4])

    #Create listening socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listen_sock:

        listen_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listen_sock.bind((listen_host, listen_port))
        listen_sock.listen()

        print(f"Proxy listening on {listen_host}:{listen_port} -> {server_host}:{server_port}")
        print(f"Using Minecraft protocol {MC_VERSION} (play state)")


        #while socket open, listen for a new client and open a thread using client  function
        while True:
            client_sock, addr = listen_sock.accept()
            print(f"New client from {addr}")
            threading.Thread(
                target=handle_client,
                args=(client_sock, server_host, server_port),
                daemon=True,
            ).start()

if __name__ == "__main__":
    main()