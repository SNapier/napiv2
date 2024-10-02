import requests, argparse, os, yaml, json

#DEAL WITH THE SELF SIGNED NAGIOS SSL
from urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#NAPIV2.PY
#SNAPIER

#SCRIPT DEFINITION
cname = "napiv2.py"
cversion = "0.0.2"

#WHERE IS THE SCRIPT RUNNING
appPath = os.path.dirname(os.path.realpath(__file__))

#NAGIOSXI_CONFIG.YAML
#NEVER STORE CREDS IN PLAIN TEXT
def creds(nsid):
    with open(appPath+"\\nagios_config.yml", "r") as yamlfile:
        try:
            data = yaml.safe_load(yamlfile)
            r = {"url":data[0]["nagios"][nsid]["url"],"un":data[0]["nagios"][nsid]["usr"],"pw":data[0]["nagios"][nsid]["pswd"]}
        except Exception as e:
            print(e)
            r = False
        finally:
            return r

#API BASIC AUTH EXAMPLE TO REQUEST AN AUTH TOKEN NAGIOSXI SERVER
def nagiosxiAuthAPI(crds):
    
    #DATA PAYLOAD
    d = {
        "username" : crds["un"],
        "password" : crds["pw"],
        "valid_min": "1" 
    }
    myurl = 'https://{}/nagiosxi/api/v1/authenticate?'.format(crds["url"])
    tkn = False
    try:
        #AUTHENTICATE OUR NAGIOSXI USER
        response = requests.post(url=myurl, data=d, verify=False)
        r = response.json()
    except Exception as e:
        print(e)
    finally:
        return r


#NAGIOSXI API V2 
def nagiosxiGenericAPIv2(myxi,myep,mycls,qry,mytkn):
    try:
        myurl = "https://{}/nagiosxi/api/v2/{}/{}?{}&token={}".format(myxi,myep,mycls,qry,mytkn)
        ## Authentication request
        response = requests.get(myurl, verify=False)
        r = response.json()
    except Exception as e:
        print(e)
    finally:    
        return r


if __name__ == "__main__" :
    
    #INPUT FROM NAGIOS
    args = argparse.ArgumentParser(prog=cname+"v:"+cversion, formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    #ARGS
    #NAGIOSXI SERVER ID, MUST EXIST IN YAML
    #NSID
    args.add_argument(
        "-n","--nsid",
        required=True,
        default=None,
        help="String(nagiosxi_server_id): NagiosXI Instance definition stored in the yml.(drs,dev,prd)."
    ),
    #ENDPOINT
    args.add_argument(
        "-e","--endpoint",
        required=True,
        default=None,
        help="String(endpoint): The NagiosXI API v2 endpoint."
    ),
    #CLASS
    args.add_argument(
        "-c","--eclass",
        required=True,
        default=None,
        help="String(endpoint_class): The NagiosXI API v2 class that is to be exercised."
    ),
    #QUERY STRING
    args.add_argument(
        "-q","--eqry",
        required=False,
        default=None,
        help="String(nagiosxi_lmtd_query): A manually formatted limited query string passed to the endpoint class."
    )
    #PRETTY PRINT
    args.add_argument(
        "-p",
        required=False,
        default=None,
        action="store_true",
        help="Boolean(True/False): If argument evaluates true, the result json will be printed in human readable format.")

    #PARSE ARGS
    meta = args.parse_args()

    #GET CREDS FROM YAML
    crds = creds(meta.nsid)

    #NOTHING UP MY SLEEVE
    x = False
    apirsp = False

    #WHATCHA DOING?
    try:
        #AUTHENTICATE AND GET LOGIN TOKEN
        x = nagiosxiAuthAPI(crds)
        
        #SUCCESS
        if x:
            mytkn = x["auth_token"]
            myxi = crds["url"]
            myep = meta.endpoint
            mycls = meta.eclass

            #QUERY IS NOT REQUIRED
            if meta.eqry != "":
                qry = meta.eqry
            else:
                qry = ""

            #NAGIOSXI LIMITED SEARCH QUERIES
            #qry = "&name=in:localhost,host1,host2,u2204ncpa"

            #SINGLE RESULTS FAIL
            #qry = "&name=localhost"
            
            #V2 GENERIC API QUERY    
            apirsp = nagiosxiGenericAPIv2(myxi,myep,mycls,qry,mytkn)

    #PROBLEM IN ENGINEERING CAPTAIN
    except Exception as e:
        print(e)
    
    #THE OUTRO
    finally:            
        
        #WHAT HAD HAPPENED WAS
        if "auth_token" in x.keys():
            
            #TELL HEM WHO YOU ARE, WHY YOU ARE HERE, AND WHAT DROIDS YOU'RE LOOKING FOR.
            print("username={}; endpoint={}; class={};".format(x["username"],meta.endpoint,meta.eclass))

            #ENDPOINTS HAVE MULTIPLE CLASSES
            if apirsp:
                #WE ARE EXPECTING A DICT BUT NOT EVERYTHING RETURNS ONE
                if type(apirsp) == dict:
                    
                    #TRAP MESSAGE, THIS INDICATES WE SENT AN INVALID OR MALFORMED QUERY TO THE API
                    if "message" in apirsp.keys():
                        print(apirsp["message"])
                    
                    #PLAYGROUND FOR RESPONSE
                    else:
                        if meta.p:
                            #JSON RESULT
                            print(json.dumps(apirsp, indent=4))
                        else:
                            print(apirsp)

                #NOT A DICT? WHY NOT A DICT?
                else:
                    #WHAT AM I?
                    rtype = type(apirsp)
                    print("RESULT_TYPE={}".format(rtype))
                    
                    #I'M A LIST
                    if rtype == list:
                        #NICE FORMAT THE LIST
                        for i in apirsp:
                            print(i)                       
                    #STRING, MAYBE?
                    else:
                        #STRINGIFY AND PRINT ME
                        print(str(apirsp))


        #DIDNT WORK DUDE!
        else:
            print("AUTHENTICATION FALED")