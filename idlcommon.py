
def getDllMethodExternalName(interface, m):
    return "%s_%s" % (interface.name, m.name)
