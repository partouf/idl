
def getDllMethodExternalNameByName(interface, name):
    return "%s_%s" % (interface.name, name)

def getDllMethodExternalName(interface, m):
    return getDllMethodExternalNameByName(interface, m.name)
