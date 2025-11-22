from minebase import load_version, Edition # type: ignore

"""
Test File to explore minecraft packet ids and their matching name. Can be adjusted to different minecraft versions


"""


def getPacketName(version_info, state, direction):
    """
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

def main():
    #Change MC version as needed
    version = "1.21.6"
    vinfo = load_version(version, Edition.PC)

    c2s_play = getPacketName(vinfo, "play", "toServer")
    s2c_play = getPacketName(vinfo, "play", "toClient")

    print("Client -> Server (play state):")
    for pid, name in sorted(c2s_play.items()):
        print(f"  {pid:3d}: {name}")

    print("\nServer -> Client (play state):")
    for pid, name in sorted(s2c_play.items()):
        print(f"  {pid:3d}: {name}")

if __name__ == "__main__":
    main()