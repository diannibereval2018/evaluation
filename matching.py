import sys,os,re
from utils.metricas import precision,recall,f1score
from utils.brat import generate_ann
##################################################################################################
#
#	This script requires two folders:
#	-	argv[1] = goal standard / any other file
#	-	argv[2] = system annotation / any other file
#
#	The evaluation will be carried out according to the files that are in both folders.
#
#
##################################################################################################

if len(sys.argv)<3:
    print("##################################################################################################\n\
#\n\
#	This script requires two folders:\n\
#	-	argv[1] = goal standard / any other file\n\
#	-	argv[2] = system annotation / any other file\n\
#\n\
#	The evaluation will be carried out according to the files that are in both folders.\n\
#\n\
#\n\
##################################################################################################")
    sys.exit()

if not os.path.exists(sys.argv[1]):
    print("Check Goal path: ",sys.argv[1])
    sys.exit()
if not os.path.exists(sys.argv[2]):
    print("Check System path: ",sys.argv[2])
    sys.exit()


system_files = os.listdir(sys.argv[2])
gs_files     = os.listdir(sys.argv[1])

gs_text = []
system_text = []


global_system_anotations    = {
                "Disability":           {"fp":0, "tp":0,"fn":0},
                "Scope":                {"fp":0, "tp":0,"fn":0},
                "Neg":                  {"fp":0, "tp":0,"fn":0},
                "Disability+Scope+Neg": {"fp":0, "tp":0,"fn":0},
                "Disability+(Disability+Scope+Neg)": {"fp":0, "tp":0,"fn":0},
                "Disability-Scope+Neg": {"fp":0, "tp":0,"fn":0}
                            }			
errors = []
print("\n\n")
for fi in gs_files:
    print(fi)
    gs_text = open(sys.argv[1]+"/"+fi,"rb").read().decode("utf-8").strip().replace(" , ",", ").replace(" _ "," _").replace(" %","%").replace(" . ",". ").replace(" ) ",") ").replace(" ( "," (").replace(" : ",": ").replace(" ; ","; ").split("\n")
    try:
        system_text = open(sys.argv[2]+"/"+fi,"rb").read().decode("utf-8").strip().replace(" , ",", ").replace(" _ "," _").replace(" %","%").replace(" . ",". ").replace(" ) ",") ").replace(" ( "," (").replace(" : ",": ").replace(" ; ","; ").split("\n")
    except:
        print("LOG: File Not found: "+sys.argv[2]+"/"+fi)
        errors.append("File Not found: "+sys.argv[2]+"/"+fi)
        continue
    if not len(gs_text)==len(system_text):
        print("LOG: Files must have the same number of lines:")
        print(sys.argv[1]+"/"+fi)
        print(sys.argv[2]+"/"+fi)
        errors.append("Files must have the same number of lines:"+sys.argv[2]+"/"+fi)
        continue

    def check(an_disa, an_system, term,acum):
        for an in list(an_disa):
            if an in an_system:
                an_system.remove(an)
                an_disa.remove(an)
                if acum:
                    global_system_anotations["Disability+(Disability+Scope+Neg)"]["tp"]+=1
                global_system_anotations[term]["tp"] += 1
            else:
                if acum:
                    global_system_anotations["Disability+(Disability+Scope+Neg)"]["fn"]+=1
                global_system_anotations[term]["fn"] += 1

        if acum:
            global_system_anotations["Disability+(Disability+Scope+Neg)"]["fp"]+=len(an_system)
        global_system_anotations[term]["fp"] += len(an_system)


    for l in range(len(gs_text)):
        #Disability, Scope, Neg
        for term in ["Disability","Scope","Neg"]:
            an_disa    = [linea for linea in generate_ann(gs_text[l]).strip().split("\n")     if not linea=="" and term in linea.split("\t")[1]]
            an_system  = [linea for linea in generate_ann(system_text[l]).strip().split("\n") if not linea=="" and term in linea.split("\t")[1]]
            check(an_disa,an_system,term,False)


        #Disability-Scope+Neg
        an_disa    = [linea for linea in generate_ann(gs_text[l]).strip().split("\n")     if not linea==""  ]
        a_eliminar = [(int(line.split("\t")[1].split(" ")[1]),int(line.split("\t")[1].split(" ")[2])) for line in an_disa if "Scope" in line]
        an_system  = [linea for linea in generate_ann(system_text[l]).strip().split("\n")   if not linea=="" and "Disability" in linea.split("\t")[1]]
        for elem in [an_disa,an_system]:
            for item in elem:
                    tab = item.split("\t")[1].split(" ")
                    for i_x, f_x in a_eliminar:
                        if i_x<=int(tab[1]) and f_x>=int(tab[2]) and item in elem:
                            elem.remove(item)
        an_disa = [ a for a in an_disa if "Disability" in a]
        check(an_disa, an_system, "Disability-Scope+Neg",True)


        # Disability+Scope+Neg
        an_disa   = re.findall(r'(\<scp\>(.+?)\<\/scp\>)',gs_text[l])
        an_system = re.findall(r'(\<scp\>(.+?)\<\/scp\>)',system_text[l])
        check(an_disa, an_system, "Disability+Scope+Neg",True)


print("\n\n\nResults:")
for x in ["Disability","Disability+(Disability+Scope+Neg)","Disability+Scope+Neg"]:
    print("=========================================================")
    print(x+":")
    print("---------------------------------------------------------")
    print(global_system_anotations[x])
    print("Precision:",precision(global_system_anotations[x]["tp"],global_system_anotations[x]["fp"]))
    print("Recall:",   recall(global_system_anotations[x]["tp"],global_system_anotations[x]["fn"]))
    print("F1 score:",f1score(global_system_anotations[x]["tp"],global_system_anotations[x]["fp"],global_system_anotations[x]["fn"]))
    print("=========================================================")

if not len(errors)==0:
    print(str(len(errors))+" files not evaluated.")
    print("\n- ".join(errors))

