from cybox.core import Object, Observable, ObservableComposition
from cybox.objects.file_object import File
from cybox.objects.address_object import Address
from cybox.objects.hostname_object import Hostname
from cybox.objects.uri_object import URI
from cybox.objects.pipe_object import Pipe
from cybox.objects.mutex_object import Mutex
from cybox.objects.artifact_object import Artifact
from cybox.objects.memory_object import Memory
from cybox.objects.email_message_object import EmailMessage, EmailHeader, Attachments
from cybox.objects.domain_name_object import DomainName
from cybox.objects.win_registry_key_object import *
from cybox.common import Hash, ByteRun, ByteRuns
from cybox.objects.http_session_object import *
from cybox.objects.as_object import AutonomousSystem
from stix.extensions.test_mechanism.snort_test_mechanism import *
import ntpath, socket, sys
from stix.indicator import Indicator

this_module = sys.modules[__name__]

simple_type_to_method = {}
simple_type_to_method.update(dict.fromkeys(["md5", "sha1", "sha256", "filename", "filename|md5", "filename|sha1", "filename|sha256", "malware-sample", "attachment"], "resolveFileObservable"))
simple_type_to_method.update(dict.fromkeys(["ip-src", "ip-dst"], "generateIPObservable"))
simple_type_to_method.update(dict.fromkeys(["regkey", "regkey|value"], "generateRegkeyObservable"))
simple_type_to_method.update(dict.fromkeys(["hostname", "domain", "url", "AS", "mutex", "named pipe", "link"], "generateSimpleObservable"))
simple_type_to_method.update(dict.fromkeys(["email-src", "email-dst", "email-subject"], "resolveEmailObservable"))
simple_type_to_method.update(dict.fromkeys(["http-method", "user-agent"], "resolveHTTPObservable"))
simple_type_to_method.update(dict.fromkeys(["pattern-in-file", "pattern-in-traffic", "pattern-in-memory"], "resolvePatternObservable"))

# mapping for the attributes that can go through the simpleobservable script
misp_cybox_name = {"domain" : "DomainName", "hostname" : "Hostname", "url" : "URI", "AS" : "AutonomousSystem", "mutex" : "Mutex", "named pipe" : "Pipe", "link" : "URI"}
cybox_name_attribute = {"DomainName" : "value", "Hostname" : "hostname_value", "URI" : "value", "AutonomousSystem" : "number", "Pipe" : "name", "Mutex" : "name"}
misp_indicator_type = {"domain" : "Domain Watchlist", "hostname" : "Domain Watchlist", "url" : "URL Watchlist", "AS" : "", "mutex" : "Host Characteristics", "named pipe" : "Host Characteristics", "link" : ""}

def generateObservable(indicator, attribute):
    if (attribute["type"] in ("snort", "yara")):
        generateTM(indicator, attribute)
    else:
        observable = None;
        if (attribute["type"] in simple_type_to_method.keys()):
            action = getattr(this_module, simple_type_to_method[attribute["type"]], None)
            if (action != None):
                property = action(indicator, attribute)
		property.condition = "Equals"
                object = Object(property)
                object.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":" + property.__class__.__name__ + "-" + attribute["uuid"]
                observable = Observable(object)
                observable.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":observable-" + attribute["uuid"]
                indicator.add_observable(observable)

def resolveFileObservable(indicator, attribute):
    hashValue = ""
    filenameValue = ""
    if (attribute["type"] in ("filename|md5", "filename|sha1", "filename|sha256", "malware-sample")):
        values = attribute["value"].split('|')
        filenameValue = values[0]
        hashValue = values[1]
        indicator.add_indicator_type("File Hash Watchlist")
    else:
        if (attribute["type"] in ("filename", "attachment")):
            filenameValue = attribute["value"]
        else:
            hashValue = attribute["value"]
            indicator.add_indicator_type("File Hash Watchlist")
    observable = generateFileObservable(filenameValue, hashValue)
    return observable

def generateFileObservable(filenameValue, hashValue):
    file_object = File()
    if (filenameValue != ""):
        if (("/" in filenameValue) or ("\\" in filenameValue)):
            file_object.file_path = ntpath.dirname(filenameValue)
            file_object.file_name = ntpath.basename(filenameValue)
        else:
            file_object.file_name = filenameValue
    if (hashValue != ""):
        file_object.add_hash(Hash(hash_value=hashValue, exact=True))
    return file_object

def generateIPObservable(indicator, attribute):
    indicator.add_indicator_type("IP Watchlist")
    address_object = Address()
    cidr = False
    if ("/" in attribute["value"]):
        ip = attribute["value"].split('/')[0]
        cidr = True
    else:
        ip = attribute["value"]
    try:
        socket.inet_aton(ip)
        ipv4 = True
    except socket.error:
        ipv4 = False
    if (cidr == True):
        address_object.category = "cidr"
    elif (ipv4 == True):
        address_object.category = "ipv4-addr"
    else:
        address_object.category = "ipv6-addr"
    if (attribute["type"] == "ip-src"):
        address_object.is_source = True
    else:
        address_object.is_source = False
    address_object.address_value = attribute["value"]
    return address_object

def generateRegkeyObservable(indicator, attribute):
    indicator.add_indicator_type("Host Characteristics")
    regkey = ""
    regvalue = ""
    if (attribute["type"] == "regkey|value"):
        regkey = attribute["value"].split('|')[0]
        regvalue = attribute["value"].split('|')[1]
    else:
        regkey = attribute["value"]
    reg_object = WinRegistryKey()
    reg_object.key = regkey
    if (regvalue != ""):
        reg_value_object = RegistryValue()
        reg_value_object.data = regvalue
        reg_object.values = RegistryValues(reg_value_object)
    return reg_object

def generateSimpleObservable(indicator, attribute):
    cyboxName = misp_cybox_name[attribute["type"]]
    constructor = getattr(this_module, cyboxName, None)
    indicatorType = misp_indicator_type[attribute["type"]]
    if (indicatorType != ""):
        indicator.add_indicator_type(indicatorType)
    new_object = constructor()
    setattr(new_object, cybox_name_attribute[cyboxName], attribute["value"])
    return new_object

def generateTM(indicator, attribute):
    if (attribute["type"] == "snort"):
        tm = SnortTestMechanism()
        tm.rules = [attribute["value"]]
    else:
        # remove the following line and uncomment the code below once yara test mechanisms get added to python-stix
        return indicator
        #tm = SnortTestMechanism()
        #tm.rules = [attribute["value"]]
    indicator.test_mechanisms = [tm]

def resolveEmailObservable(indicator, attribute):
    indicator.add_indicator_type("Malicious E-mail")
    new_object = EmailMessage()
    email_header = EmailHeader()
    if (attribute["type"] == "email-src"):
        email_header.from_ = attribute["value"]
    elif(attribute["type"] == "email-dst"):
        email_header.to = attribute["value"]
    else:
        email_header.subject = attribute["value"]
    new_object.header = email_header
    return new_object

def resolveHTTPObservable(indicator, attribute):
    request_response = HTTPRequestResponse()
    client_request = HTTPClientRequest()
    if (attribute["type"] == "user-agent"):
        header = HTTPRequestHeader()
        header_fields = HTTPRequestHeaderFields()
        header_fields.user_agent = attribute["value"]
        header.parsed_header = header_fields
        client_request.http_request_header = header
    else: 
        line = HTTPRequestLine()
        line.http_method = attribute["value"]
        client_request.http_request_line = line
    request_response.http_client_request = client_request
    new_object = HTTPSession()
    request_response.to_xml()
    new_object.http_request_response = [request_response]
    return new_object

# use this when implementing pattern in memory and pattern in traffic
def resolvePatternObservable(indicator, attribute):
    new_object = None
    if attribute["type"] == "pattern-in-file":
        byte_run = ByteRun()
        byte_run.byte_run_data = attribute["value"]
        new_object = File()
        new_object.byte_runs = ByteRuns(byte_run)
    # custom properties are not implemented in the API yet
    # elif attribute["type"] == "pattern-in-memory":
    # elif attribute["type"] == "pattern-in-traffic":
    return new_object
    
# create an artifact object for the malware-sample type.
def createArtifactObject(indicator, attribute):
    artifact = Artifact(data = attribute["data"])
    artifact.parent.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":artifact-" + attribute["uuid"]
    observable = Observable(artifact)
    observable.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":observable-artifact-" + attribute["uuid"]
    indicator.add_observable(observable)

# return either a composition if data is set in attribute, or just an observable with a filename if it's not set
def returnAttachmentComposition(attribute):
    file_object = File()
    file_object.file_name = attribute["value"]
    file_object.parent.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":file-" + attribute["uuid"]
    observable = Observable()
    if "data" in attribute:
        artifact = Artifact(data = attribute["data"])
        artifact.parent.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":artifact-" + attribute["uuid"]
        observable_artifact = Observable(artifact)
        observable_artifact.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":observable-artifact-" + attribute["uuid"]
        observable_file = Observable(file_object)
        observable_file.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":observable-file-" + attribute["uuid"]
        composition = ObservableComposition(observables = [observable_artifact, observable_file])
        observable.observable_composition = composition
    else:
        observable = Observable(file_object)
    observable.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":observable-" + attribute["uuid"]
    if attribute["comment"] != "":
        observable.description = attribute["comment"]
    return observable

# email-attachment are mapped to an email message observable that contains the attachment as a file object
def generateEmailAttachmentObject(indicator, attribute):
    file_object = File()
    file_object.file_name = attribute["value"]
    email = EmailMessage()
    email.attachments = Attachments()
    email.add_related(file_object, "Contains", inline=True)
    file_object.parent.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":file-" + attribute["uuid"]
    email.attachments.append(file_object.parent.id_)
    email.parent.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":EmailMessage-" + attribute["uuid"]
    observable = Observable(email)
    observable.id_ = cybox.utils.idgen.__generator.namespace.prefix + ":observable-" + attribute["uuid"]
    indicator.observable = observable

