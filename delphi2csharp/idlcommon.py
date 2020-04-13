
def getDllMethodExternalNameByName(interface, name):
    return "%s_%s" % (interface.name, name)

def getDllMethodExternalName(interface, m):
    return getDllMethodExternalNameByName(interface, m.name)

def getDllLoadMethodExternalName(module):
    return "%s_Load" % (module.name)

def getDllExceptionMethodExternalName(module, excdetail):
    return '%sGetException%s' % (module.name, excdetail)
